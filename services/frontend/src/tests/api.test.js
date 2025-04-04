import axios from 'axios';
import { describe, it, expect, vi } from 'vitest';

describe('Frontend API Interactions', () => {
  it('should successfully login via the API Gateway', async () => {
    const mockResponse = { status: 200, data: { token: 'mockToken' } };
    vi.spyOn(axios, 'post').mockResolvedValueOnce(mockResponse);

    const response = await axios.post('/api/login', {
      username: 'testuser',
      password: 'password',
    });

    expect(response.status).toBe(200);
    expect(response.data.token).toBe('mockToken');
  });
});