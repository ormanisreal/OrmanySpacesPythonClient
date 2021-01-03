from orman import OrmanNameSpace

alias='helfei'
reg_code='breadmaker'
password='my-local-secret-pass'

print("## Test 1 - register namespace")
orman = OrmanNameSpace()
code = orman.register(alias, reg_code, password)
if code == 201:
    print("      └──PASS")

print("## Test 2 - encrypt namespace")
ens = orman.encrypt( orman.ns() )
if 'aeskey' in ens:
    print("           └──PASS")

print("## Test 3 - reinstantiate and decrypt namespace")
orman = OrmanNameSpace()
orman.ns()
dns = orman.decrypt(ens)
if 'pubKey' in dns:
    print(" └──PASS")

print("## Test 4 - save namespace locally")
orman.save(dns)
print(" └──PASS")

print("## Test 5 - get auth token")
token = orman.token()
print( "  └─%s\n    └──PASS" % (token) )

print("## Test 6 - test auth token")
r = orman.test(token)
print( "       └──%s" % str(r) )
if "Welcome" in r["response"]:
    print("          └──PASS")

print("## Test 7 - save local ns to cloud")
ns = orman.ns()
ns["nspace"] = {
    "message": "My super secret dictionary."
}
orman.sync(ns)
print("        └──PASS")

print("## Test 8 - save cloud ns to local")
orman.save( orman.sync() )
print("            └──PASS")

print("## Test 9 - see if our super secret dictionary saved")
ns = OrmanNameSpace().ns()
message = ns["nspace"]["message"]
if "secret" in message:
    print("    %s\n            └──PASS" % (message))
    
print("## Test 10 - delete ns locally and cloud")
orman = OrmanNameSpace()
token = orman.token()
r = orman.delete(alias, reg_code, token, 'delete')
if r.status_code == 203:
    print("         └──Victory mother fucker")
else:
    print(r.status_code)