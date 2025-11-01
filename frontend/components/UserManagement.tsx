import { useEffect, useState } from "react";
import { getCurrentUser, loginUser, logoutUser, registerUser } from "../services/UserService";

export default function UserManagement() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loggedInUser, setLoggedInUser] = useState("");
    
    useEffect(() => {
      const initAuth = async () => {
        try {
          const user = await getCurrentUser();

          if (user) {
            setLoggedInUser(user.username);
            setIsLoggedIn(true);
          }
        } catch {
            setIsLoggedIn(false);
        }
      };
      initAuth();
    }, []);

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!username.trim() || !password) {
            return; // TODO Warn user or something...
        }

        try {
            const loginResult = await loginUser(username, password);

            if (loginResult != null) {
                window.location.reload();
                // TODO Instead of reloading the whole page/app, how to trigger update in other controls? Ex. Show favourite icons on recipes

                // setLoggedInUser(username);
                // setIsLoggedIn(true);
                console.log("Login successful");
            }

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
            const result = await registerUser(username, password);

            if (result) {
                console.log("User ${}")
            }
        } catch (error) {
            console.error("Error with registration: ", error);
        }
    }

    const handleLogout = async (e: React.MouseEvent) => {
        e.preventDefault();

        try {
            await logoutUser();
            window.location.reload();
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
                    <p className='inline-flex  items-center border-primary text-gray-900 m-3'>{loggedInUser}</p>
                    <button className='btn btn-primary m-3 text-white hover:bg-opacity-90' onClick={handleLogout}>Log Out</button>
                </div>)}
        </div>
    )
}