import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, it, vi } from 'vitest';
import ToastContainer from '../components/ToastContainer';
import UserManagement from '../components/UserManagement';
import { AuthProvider } from '../context/AuthContext';
import { ToastProvider } from '../context/ToastContext';
import { api } from '../services/apiService';
import { getAccessToken, loginUser, logoutUser, refreshAccessToken } from '../services/UserService';

vi.mock('../services/apiService', () => ({
  api: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}));

const tokenResponse = { data: { access_token: 'access-token', token_type: 'bearer' } };

afterEach(() => vi.resetAllMocks());

it.each([true, false])('clears the local session and reports logout failure (server success: %s)', async (success) => {
  vi.mocked(api.post).mockResolvedValueOnce(tokenResponse);
  await loginUser('Cook', 'password');
  vi.mocked(api.get).mockResolvedValueOnce({ data: { username: 'Cook' } });
  if (success) {
    vi.mocked(api.delete).mockResolvedValueOnce({ status: 204 });
  } else {
    vi.mocked(api.delete).mockRejectedValueOnce(new Error('Server unavailable'));
  }

  const user = userEvent.setup();
  render(
    <AuthProvider>
      <ToastProvider>
        <UserManagement />
        <ToastContainer />
      </ToastProvider>
    </AuthProvider>
  );

  await user.click(await screen.findByRole('button', { name: 'Log Out' }));

  expect(await screen.findByRole('button', { name: 'Login' })).toBeInTheDocument();
  expect(api.delete).toHaveBeenCalledWith('/auth/tokens/current');
  expect(getAccessToken()).toBeNull();
  const warning = 'You signed out on this page, but the server session could not be ended.';
  if (success) {
    expect(screen.queryByText(warning)).toBeNull();
  } else {
    expect(await screen.findByText(warning)).toBeInTheDocument();
  }
  expect(await refreshAccessToken()).toBe(false);
  expect(api.post).toHaveBeenCalledTimes(1);
});

it('discards an in-flight refresh during logout and allows a new sign-in', async () => {
  vi.mocked(api.post).mockResolvedValueOnce(tokenResponse);
  await loginUser('Cook', 'password');

  let completeRefresh!: () => void;
  vi.mocked(api.post).mockImplementationOnce(() => new Promise((resolve) => {
    completeRefresh = () => resolve(tokenResponse);
  }));
  vi.mocked(api.delete).mockResolvedValueOnce({ status: 204 });

  const refresh = refreshAccessToken();
  const logout = logoutUser();
  expect(getAccessToken()).toBeNull();
  expect(api.delete).not.toHaveBeenCalled();

  completeRefresh();
  expect(await refresh).toBe(false);
  await logout;
  expect(getAccessToken()).toBeNull();

  vi.mocked(api.post).mockResolvedValueOnce(tokenResponse);
  expect(await loginUser('Cook', 'password')).toBe(true);
  expect(getAccessToken()).toBe('access-token');
  vi.mocked(api.post).mockResolvedValueOnce(tokenResponse);
  expect(await refreshAccessToken()).toBe(true);
});
