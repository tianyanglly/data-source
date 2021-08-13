db.createUser(
  {
    user: "admin",
    pwd: "shvh44mk7zdi7zjrjm",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)

db.createUser(
  {
    user: "djOnline",
    pwd: "xxwc4hlhcr7b1reu58",
    roles: [ { role: "readWrite", db: "djData" },
             { role: "readWrite", db: "djDataStable" } ]
  }
)

scrapydweb
YIabrGuVqdavgM5O