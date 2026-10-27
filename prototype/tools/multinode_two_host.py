"""Explicit private two-host TLS acceptance drill. No external business effects.
Run orchestrate only in the authorized PRAIN-DEV test environment.
"""
import argparse, base64, hashlib, hmac, json, os, pathlib, shutil, signal, ssl
import subprocess, sys, tarfile, time, uuid
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from prain.scf_http import SCFHTTPReceiver, serve, send, receipt_fields, receipt_signature
from prain.scf_wire import sign_envelope
from prain.scf_delivery import SCFDeliveryQueue
from prain.durable_semantics import DurableSemanticFabric

def execute(args, **kw):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=30, **kw)

def envelope(config, message_id, bad_key=False):
    now = datetime.now(timezone.utc)
    key = base64.b64decode(config["peer_key"])
    claim = dict(claim_id=message_id, subject="two-host-fixture", predicate="state",
        value="ready", scope="acceptance", source=config["origin"],
        evidence_refs=["synthetic-test-evidence"], confidence=0.9,
        observed_at=(now-timedelta(seconds=2)).isoformat(),
        valid_until=(now+timedelta(minutes=5)).isoformat())
    return sign_envelope(key=b"x"*32 if bad_key else key, message_id=message_id,
        origin_node=config["origin"], destination_node=config["destination"],
        tenant="acceptance", issued_at=(now-timedelta(seconds=2)).isoformat(),
        expires_at=(now+timedelta(minutes=4)).isoformat(),
        payload={"claim":claim,"scope":"acceptance"})

def read_config(path):
    return json.loads(pathlib.Path(path).read_text())

def server(config_path):
    c = read_config(config_path); root=pathlib.Path(c["root"])
    class Receiver(SCFHTTPReceiver):
        def accept(self, body, now):
            result=super().accept(body,now)
            if body["message_id"].startswith("crash-") and not (root/"crash-once").exists():
                (root/"crash-once").write_text("commit-before-ack")
                os._exit(73)
            return result
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(root/c["cert"],root/c["cert_key"])
    receiver=Receiver(db_path=str(root/"receiver.sqlite"),node_id=c["node"],
        tenant="acceptance",peer_keys={c["peer"]:base64.b64decode(c["peer_key"])})
    service=serve(receiver,host=c["address"],port=c["port"],ssl_context=context)
    (root/"server.pid").write_text(str(os.getpid()))
    (root/"ready.json").write_text(json.dumps({"pid":os.getpid(),"node":c["node"],
        "address":c["address"],"port":service.server_port,"hostname":os.uname().nodename}))
    service.serve_forever(poll_interval=0.05)

def worker_send(config_path):
    c=read_config(config_path); root=pathlib.Path(c["root"])
    env=envelope(c,"reverse-"+uuid.uuid4().hex)
    result=send(c["endpoint"],env,ssl_context=ssl.create_default_context(cafile=str(root/"ca.crt")),timeout=4)
    expected=receipt_fields(env,result["receipt"]["result"])
    assert expected==result["receipt"]
    assert hmac.compare_digest(result["receipt_signature"],receipt_signature(expected,base64.b64decode(c["peer_key"])))
    print(json.dumps({"verified":True,"decision":result["decision"],"hostname":os.uname().nodename}))

def orchestrate(args):
    source=pathlib.Path(args.source).resolve()
    result_root=pathlib.Path(args.results).resolve(); result_root.mkdir(parents=True,exist_ok=True)
    run_id="two-host-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:6]
    root=result_root/run_id; root.mkdir(mode=0o700)
    node_b="/opt/prain-test/"+run_id
    ssh=["ssh","-i",args.ssh_key,"-o","UserKnownHostsFile="+args.known_hosts,
        "-o","StrictHostKeyChecking=yes","-o","BatchMode=yes","-o","ConnectTimeout=5","root@10.77.0.2"]
    processes=[]; cases=[]; start=time.monotonic()
    partition_rule=["iptables","-I","INPUT","-s","10.77.0.3","-p","tcp","--dport","18443","-j","REJECT","--reject-with","tcp-reset"]
    unpartition_rule=["iptables","-D","INPUT","-s","10.77.0.3","-p","tcp","--dport","18443","-j","REJECT","--reject-with","tcp-reset"]
    partition_installed=False
    def remote(command):
        import shlex
        return execute(ssh+[shlex.join(command)])
    def record(name, fn):
        began=time.monotonic()
        detail=fn()
        cases.append({"case":name,"status":"PASS","seconds":round(time.monotonic()-began,6),"detail":detail})
    def launch_b():
        remote(["rm","-f",node_b+"/ready.json"])
        p=subprocess.Popen(ssh+["python3 "+node_b+"/tools/multinode_two_host.py serve "+node_b+"/config.json"],
            stdout=(root/"node-b-server.log").open("a"),stderr=subprocess.STDOUT)
        processes.append(p)
        for _ in range(50):
            try: return json.loads(remote(["cat",node_b+"/ready.json"]).stdout)
            except subprocess.CalledProcessError:time.sleep(.1)
        raise RuntimeError("node_b_not_ready")
    try:
        (root/"tools").mkdir(); shutil.copy2(__file__,root/"tools/multinode_two_host.py")
        shutil.copytree(source/"prain",root/"prain",ignore=shutil.ignore_patterns("__pycache__"))
        execute(["openssl","req","-x509","-newkey","rsa:2048","-nodes","-keyout",str(root/"ca.key"),
            "-out",str(root/"ca.crt"),"-days","1","-subj","/CN=PRAIN ephemeral acceptance CA"])
        for name,address in (("a","10.77.0.3"),("b","10.77.0.2")):
            execute(["openssl","req","-newkey","rsa:2048","-nodes","-keyout",str(root/(name+".key")),
                "-out",str(root/(name+".csr")),"-subj","/CN="+address])
            (root/(name+".ext")).write_text("subjectAltName=IP:"+address+"\nextendedKeyUsage=serverAuth\n")
            execute(["openssl","x509","-req","-in",str(root/(name+".csr")),"-CA",str(root/"ca.crt"),
                "-CAkey",str(root/"ca.key"),"-CAcreateserial","-out",str(root/(name+".crt")),
                "-days","1","-extfile",str(root/(name+".ext"))])
        key=os.urandom(32)
        common={"peer_key":base64.b64encode(key).decode(),"port":18443}
        a={**common,"root":str(root),"node":"node-a","peer":"node-b","address":"10.77.0.3",
            "cert":"a.crt","cert_key":"a.key","origin":"node-a","destination":"node-b",
            "endpoint":"https://10.77.0.2:18443/scf/v1/receive"}
        b={**common,"root":node_b,"node":"node-b","peer":"node-a","address":"10.77.0.2",
            "cert":"b.crt","cert_key":"b.key","origin":"node-b","destination":"node-a",
            "endpoint":"https://10.77.0.3:18443/scf/v1/receive"}
        (root/"config.json").write_text(json.dumps(a))
        (root/"b-config.json").write_text(json.dumps(b))
        package=root/"node-b.tar"
        with tarfile.open(package,"w") as tar:
            for item in ["tools","prain","ca.crt","b.crt","b.key"]:tar.add(root/item,arcname=item)
            tar.add(root/"b-config.json",arcname="config.json")
        remote(["mkdir","-p","-m","700",node_b])
        scp=["scp","-i",args.ssh_key,"-o","UserKnownHostsFile="+args.known_hosts,
             "-o","StrictHostKeyChecking=yes","-o","BatchMode=yes",str(package),"root@10.77.0.2:"+node_b+"/package.tar"]
        execute(scp);remote(["tar","-xf",node_b+"/package.tar","-C",node_b])
        a_process=subprocess.Popen([sys.executable,str(root/"tools/multinode_two_host.py"),"serve",str(root/"config.json")],
            stdout=(root/"node-a-server.log").open("w"),stderr=subprocess.STDOUT)
        processes.append(a_process)
        for _ in range(100):
            if (root/"ready.json").exists():break
            if a_process.poll() is not None:raise RuntimeError("node_a_exited")
            time.sleep(.05)
        ready_a=read_config(root/"ready.json");ready_b=launch_b()
        assert ready_a["hostname"]!=ready_b["hostname"]
        context=ssl.create_default_context(cafile=str(root/"ca.crt"))
        def delivery(env):
            reply=send(a["endpoint"],env,ssl_context=context,timeout=3)
            fields=receipt_fields(env,reply["receipt"]["result"])
            assert fields==reply["receipt"] and hmac.compare_digest(reply["receipt_signature"],receipt_signature(fields,key))
            assert reply["decision"]=="adopt"
            return reply
        normal=envelope(a,"normal-"+uuid.uuid4().hex)
        record("A_to_B_TLS_authenticated_receipt",lambda:{"claim_id":delivery(normal)["claim_id"],"receiver":ready_b})
        record("B_to_A_TLS_authenticated_receipt",lambda:json.loads(remote(["python3",node_b+"/tools/multinode_two_host.py","send",node_b+"/config.json"]).stdout))
        record("duplicate_delivery",lambda:{"claim_id":delivery(normal)["claim_id"]})
        def negative_tls():
            from urllib.error import URLError
            try:send(a["endpoint"],normal,ssl_context=ssl.create_default_context(),timeout=3)
            except URLError:return {"untrusted_ca_rejected":True}
            raise AssertionError("untrusted_certificate_accepted")
        record("untrusted_certificate",negative_tls)
        def negative_signature():
            from urllib.error import HTTPError
            try:delivery(envelope(a,"bad-signature",True))
            except HTTPError as e:
                assert e.code==400
                return {"http_status":e.code}
            raise AssertionError("bad_signature_accepted")
        record("invalid_signature",negative_signature)
        def wrong_destination():
            from urllib.error import HTTPError
            forged=envelope({**a,"destination":"unknown-node"},"wrong-destination-"+uuid.uuid4().hex)
            try:delivery(forged)
            except HTTPError as e:
                assert e.code==400
                return {"http_status":e.code,"rejected":True}
            raise AssertionError("wrong_destination_accepted")
        record("wrong_destination_identity",wrong_destination)
        # Check B's certificate against a wrong name on the same private route.
        def wrong_b_hostname():
            import http.client
            with __import__("socket").create_connection(("10.77.0.2",18443),timeout=3) as sock:
                with context.wrap_socket(sock,server_hostname="incorrect.invalid"):
                    pass
        def negative_hostname():
            try:wrong_b_hostname()
            except ssl.SSLCertVerificationError:return {"hostname_mismatch_rejected":True}
            raise AssertionError("wrong_tls_hostname_accepted")
        record("wrong_TLS_peer_hostname",negative_hostname)
        q=SCFDeliveryQueue(str(root/"sender.sqlite"))
        crash=envelope(a,"crash-"+uuid.uuid4().hex)
        q.publish(crash.message_id,asdict(crash));q.claim()
        def crash_recover():
            try:delivery(crash)
            except (OSError,ConnectionError):pass
            else:raise AssertionError("expected_lost_response")
            assert q.recover()==1 and q.claim() is None
            assert q.status(crash.message_id)["status"]=="UNKNOWN"
            recovery_start=time.monotonic()
            launch_b()
            verified=delivery(crash)
            q.reconcile(crash.message_id,"SUCCEEDED","verified-receipt:"+hashlib.sha256(json.dumps(verified,sort_keys=True).encode()).hexdigest())
            assert q.status(crash.message_id)["attempts"]==1
            return {"recovery_seconds":time.monotonic()-recovery_start,"attempts":1,"receipt_verified":True}
        record("crash_after_commit_before_ack_reconcile",crash_recover)
        def inspect(expected=2):
            raw=remote(["python3",node_b+"/tools/multinode_two_host.py","inspect",node_b+"/config.json"]).stdout
            state=json.loads(raw)
            assert state["decision_count"]==expected
            return state
        record("restart_idempotent_projection_count",inspect)
        def scoped_partition():
            nonlocal partition_installed
            blocked=envelope(a,"partition-"+uuid.uuid4().hex)
            before=inspect()["decision_count"]
            try:
                remote(partition_rule);partition_installed=True
                try:delivery(blocked)
                except (OSError,ConnectionError):pass
                else:raise AssertionError("packet_filter_did_not_block")
            finally:
                if partition_installed:
                    remote(unpartition_rule);partition_installed=False
            assert inspect()["decision_count"]==before
            verified=delivery(blocked)
            assert inspect(before+1)["decision_count"]==before+1
            return {"filter":"B INPUT from A TCP/18443 REJECT","outage_rejected":True,
                    "recovery_receipt_verified":True,"decisions_before":before,"decisions_after":before+1,
                    "claim_id":verified["claim_id"]}
        record("private_port_packet_filter_cut_restore",scoped_partition)
        result={"verdict":"PASS_DECLARED_SCOPE","run_id":run_id,"cases":cases,
            "topology":{"node_a":ready_a,"node_b":ready_b,"transport":"private IP TLS plus HMAC envelopes/receipts"},
            "duration_seconds":time.monotonic()-start,
            "source_sha256":{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((source/"prain").glob("*.py"))},
            "limits":["two hosts, one message receiver on each","single-direction scoped TCP port filter cut, not full network partition",
            "synthetic SCF projections, no external business effect","shared-key authentication, not mTLS or independent signer",
            "no distributed consensus or production-wide approval","backup RPO not measured"]}
        (root/"result.json").write_text(json.dumps(result,indent=2))
        print(json.dumps({"result_file":str(root/"result.json"),"verdict":result["verdict"],"cases":len(cases)}))
    except BaseException as e:
        (root/"result.json").write_text(json.dumps({"verdict":"FAIL","cases":cases,"error":type(e).__name__+":"+str(e)},indent=2))
        raise
    finally:
        if partition_installed:
            try:remote(unpartition_rule)
            except Exception:pass
        try:remote(["python3","-c","import os,pathlib,signal; p=pathlib.Path("+repr(node_b+"/server.pid")+"); os.kill(int(p.read_text()),signal.SIGTERM) if p.exists() else None"])
        except Exception:pass
        for p in processes:
            if p.poll() is None:p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        # Remove ephemeral secrets after all listeners have stopped.
        for name in ["a.key","b.key","ca.key","config.json","b-config.json","node-b.tar"]:
            (root/name).unlink(missing_ok=True)
        try:remote(["rm","-f",node_b+"/b.key",node_b+"/config.json",node_b+"/package.tar"])
        except Exception:pass

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=["orchestrate","serve","send","inspect"]);parser.add_argument("config",nargs="?")
    parser.add_argument("--source");parser.add_argument("--results");parser.add_argument("--ssh-key");parser.add_argument("--known-hosts")
    args=parser.parse_args()
    if args.mode=="serve":server(args.config)
    elif args.mode=="send":worker_send(args.config)
    elif args.mode=="inspect":
        c=read_config(args.config); f=DurableSemanticFabric(str(pathlib.Path(c["root"])/"receiver.sqlite"))
        print(json.dumps({"decision_count":len(f.decisions()),"hostname":os.uname().nodename,"db":"receiver.sqlite"}))
    else:orchestrate(args)

