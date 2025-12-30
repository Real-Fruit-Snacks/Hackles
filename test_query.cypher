# Finds enabled users with Service Principal Names (SPNs) that are vulnerable to Kerberoasting attacks
MATCH (u:User)
WHERE u.enabled = true
AND u.hasspn = true
RETURN u.name AS username, u.displayname AS displayname, u.enabled AS enabled
LIMIT 10
