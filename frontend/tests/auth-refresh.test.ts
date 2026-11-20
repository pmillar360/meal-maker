import { expect, it, vi } from 'vitest';
import { getAccessToken, refreshAccessToken } from '../services/UserService';
import { api } from '../services/apiService';

vi.mock('../services/apiService', () => ({
  api: { post: vi.fn() },
}));

it('shares one rotation request between simultaneous refresh callers', async () => {
  vi.mocked(api.post).mockResolvedValueOnce({
    data: { access_token: 'new-token', token_type: 'bearer' },
  });

  const results = await Promise.all([refreshAccessToken(), refreshAccessToken()]);

  expect(results).toEqual([true, true]);
  expect(api.post).toHaveBeenCalledTimes(1);
  expect(getAccessToken()).toBe('new-token');
});
