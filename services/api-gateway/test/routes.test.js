process.env.PORT = 8081; // Set the port to 8081 for testing

const request = require('supertest');
const app = require('../index');

describe('API Gateway Routes', () => {
  it('should proxy requests to the Auth Service', async () => {
    const response = await request(app)
      .post('/api/login')
      .send({ username: 'testuser', password: 'password' });

    expect(response.statusCode).toBe(200);
    // Add more assertions based on the expected response from the Auth Service
  });
});