const mysql = require('mysql');
const jsonfile = require('jsonfile');
const config = jsonfile.readFileSync('config.json')

const connection = () => mysql.createConnection({
    host: config.database.host,
    user: config.database.user,
    password: config.database.password,
    database: config.database.database,
})


module.exports = connection;