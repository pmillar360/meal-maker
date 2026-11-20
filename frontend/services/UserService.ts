import { api } from "./apiService";
import { User } from "./TypeService";
import axios from "axios";

let accessToken: string | null = null;
let pendingRefresh: Promise<boolean> | null = null;
let refreshAllowed = true;

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface UserIdentityResponse {
  username: string;
}

const setToken = (tokens: TokenResponse) => {
  accessToken = tokens.access_token;
};

const clearToken = () => {
  accessToken = null;
};

export const getAccessToken = () => accessToken;

const requestFreshAccessToken = async (): Promise<boolean> => {
  try {
    const response = await api.post<TokenResponse>(
      "/auth/tokens/refresh",
      {},
      { withCredentials: true }
    );
    if (!refreshAllowed) {
      return false;
    }
    setToken(response.data);
    return true;
  } catch (error) {
    clearToken();
    return false;
  }
};

export const refreshAccessToken = (): Promise<boolean> => {
  if (!refreshAllowed) {
    return Promise.resolve(false);
  }
  if (!pendingRefresh) {
    pendingRefresh = requestFreshAccessToken().finally(() => {
      pendingRefresh = null;
    });
  }
  return pendingRefresh;
};

export const registerUser = async (username: string, password: string) => {
  const response = await api.post<TokenResponse>(`/users`, { username, password });
  refreshAllowed = true;
  setToken(response.data);
  return response.data;
};

export const loginUser = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await api.post<TokenResponse>("/auth/tokens", { username, password });
    refreshAllowed = true;
    setToken(response.data);
    return true;
  } catch (error: any) {
    clearToken();
    if (error.response?.status === 400) {
      throw new Error("Invalid username or password");
    }
    throw new Error("Unable to connect to server");
  }
};

export const getCurrentUser = async (): Promise<User> => {
  if (!accessToken) {
    // Refresh the access token with the refresh token
    // NOTE This will run for not logged in users too? Will this cause issues? Needs testing
    const response = await refreshAccessToken();

    if (!response) {
      throw new Error("Could not refresh token")
      // TODO Return user.id = 0 user for logged in stuff? It will just save to local storage
    }
  }
  
  try {
    const response = await api.get<UserIdentityResponse>(`/users/me`);
    return {
      username: response.data.username,
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || "Failed to get user data");
    }
    throw error;
  }
};

export const logoutUser = async () => {
  refreshAllowed = false;
  clearToken();
  // Let any refresh finish rotating the cookie before the server revokes it.
  await pendingRefresh;
  await api.delete("/auth/tokens/current");
};
