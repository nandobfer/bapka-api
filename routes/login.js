const express = require('express');
const router = express.Router();

const newMysql = require('../src/database')


/* GET users listing. */
router.post('/', (request, response, next) => {    
	const data = request.body;
	const mysql = newMysql();
    
	mysql.connect();

    const table = data.type == 'cliente' ? 'clientes' : 'parceiros';
    const user_column = data.type == 'cliente' ? 'telefone' : 'email';

	
	mysql.query({
		sql: `SELECT * FROM ${table} WHERE ${user_column} = ? AND senha = ? ;`,
		timeout: 40000, // 40s
		values: [
			data[`user_${data.type}`],
			data[`password_${data.type}`],
        ]
	}, (error, results) => {
		if (error) console.error(error);
		console.log(results);

        if (!!results[0]) {
            response.json(results[0]);
        } else {
            response.json({error: 'Usuário não encontrado'})
        }
		mysql.end();
	});


});

module.exports = router;