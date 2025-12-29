import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function UserManagement() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const { isLoggedIn, user, login, register, logout } = useAuth();

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!username.trim() || !password) {
            return; // TODO Warn user or something...
        }

        try {
            await login(username, password);
        } catch (error) {
            console.error("Error logging in user:", error);
        }
    }

    const handleRegistration = async (e: React.MouseEvent) => {
        e.preventDefault();

        if (!username.trim() || !password) {
            return;
        }

        try {
            await register(username, password);
        } catch (error) {
            console.error("Error with registration: ", error);
        }
    }

    const handleLogout = async (e: React.MouseEvent) => {
        e.preventDefault();

        try {
            await logout();
        } catch (error) {
            console.error("Error logging out:", error);
        }
    }

    return (
        <div className='flex'>
            {!isLoggedIn && (
                <div>
                    <form className='flex' onSubmit={handleLogin}>
                        <input type='text' className='form-input md:flex-row m-3' value={username} placeholder='Username' onChange={(e) => setUsername(e.target.value)}></input>
                        <input type='password' className='form-input md:flex-row m-3' value={password} placeholder='Password' onChange={(e) => setPassword(e.target.value)}></input>
                        <button type='submit' className='btn btn-primary m-3 text-white hover:bg-opacity-90'>Login</button>
                        <button type='button' className='btn btn-primary m-3 text-white hover:bg-opacity-90' onClick={handleRegistration}>Register</button>
                    </form>
                </div>
            )}
            {isLoggedIn && (
                <div className='flex'>
                    <p className='inline-flex  items-center border-primary text-gray-900 m-3'>{user?.username}</p>
                    <button className='btn btn-primary m-3 text-white hover:bg-opacity-90' onClick={handleLogout}>Log Out</button>
                </div>)}
        </div>
    )
}