import { api } from "./apiService";
import { User } from "./TypeService";
import axios from "axios";

let accessToken: string | null = null;

interface TokenResponse {
  access_token: string;
  token_type: string;
}

const setToken = (tokens: TokenResponse) => {
  accessToken = tokens.access_token;
};

const clearToken = () => {
  accessToken = null;
};

export const getAccessToken = () => accessToken;

export const refreshAccessToken = async (): Promise<boolean> => {  
  try {
    const response = await api.post<TokenResponse>('/refresh', {}, {withCredentials: true});
    setToken(response.data);
    return true;
  } catch (error) {
    clearToken();
    return false;
  }
};

export const registerUser = async (username: string, password: string) => {
  const response = await api.post<TokenResponse>(`/register`, { username, password });
  setToken(response.data);
  return response.data;
};

export const loginUser = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await api.post<TokenResponse>("/token", { username, password });
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
    const response = await api.get<User>(`/me`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || "Failed to get user data");
    }
    throw error;
  }
};

export const logoutUser = async () => {
  try {
    const response = await api.post("/logout");
    
    if (response) {
      clearToken();
    }
  }
  catch (error : any) {

  }
};