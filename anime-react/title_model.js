const Pool = require('pg').Pool
const pool = new Pool({
  user: 'admin',
  host: 'localhost',
  database: 'imdb',
  password: 'password',
  port: 5433,
});

const titlesQuery = `SELECT name, url, poster_url, rating_count, rating_value FROM imdb.titles 
                    WHERE rating_count IS NOT NULL AND rating_value IS NOT NULL
                    ORDER BY rating_count DESC, rating_value DESC
                    LIMIT 10`

const getTitles = () => {
    return new Promise(function(resolve, reject) {
      pool.query(titlesQuery, (error, results) => {
        if (error) {
          reject(error)
        }
        resolve(results.rows);
      })
    }) 
  }

module.exports = {
    getTitles,
  }