import { defineConfig, loadEnv } from 'vite'
import Fastify from 'fastify'
import fs from 'fs'

const fastify = Fastify({ logger: false })

// Save dat from python
fastify.post('/plot', (req, reply) => {
    let output = {}
    if (typeof req.body === 'object') {
        fs.writeFileSync('./data/data.json', JSON.stringify(req.body))
    } else {
        fs.writeFileSync('./data/data.json', '{}')
    }
    reply.send({ok: true})
})

// Run the server!
fastify.listen({ port: 7779 }, (err, address) => {
    if (err) throw err
    console.log(`[RUNNING DATA SERVER ${address}]`)
})

export default ({ mode }) => {
    return defineConfig({
        server: {
            port: 7778
        }
    });
}
