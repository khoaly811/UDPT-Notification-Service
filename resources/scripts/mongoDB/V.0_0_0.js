db.createUser({
    user: "Toan",
    pwd: "Tu",
    roles: [{ role: "readWrite", db: "mydatabase" }]
});

use("hospital-management");
db.createCollection("users");