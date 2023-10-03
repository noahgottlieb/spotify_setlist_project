import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SpotifyAuth = () => {
    const [token, setToken] = useState('');
    const [userProfile, setUserProfile] = useState(null);

    console.log(userProfile, 'profile');

    useEffect(() => {
        // Function to extract the access token from the URL
        const getAccessTokenFromURL = () => {
            const queryParams = new URLSearchParams(window.location.hash.substr(1));
            return queryParams.get('access_token');
        };

        // Check if the user has already authenticated
        const existingToken = localStorage.getItem('spotifyToken');

        if (existingToken) {
            setToken(existingToken);
        } else {
            const accessToken = getAccessTokenFromURL();

            if (accessToken) {
                setToken(accessToken);
                localStorage.setItem('spotifyToken', accessToken);
            } else {
                // Redirect the user to Spotify's login page for authentication
                const clientID = process.env.REACT_APP_CLIENT_ID;
                const redirectURI = process.env.REACT_APP_SPOTIFY_REDIRECT_URL;
                const scope = 'user-read-private user-read-email'; // Add additional scopes as needed
                const authURL = `${
                    process.env.REACT_APP_AUTH_URL
                }?client_id=${clientID}&redirect_uri=${encodeURIComponent(
                    redirectURI
                )}&scope=${encodeURIComponent(scope)}&response_type=token`;

                window.location.href = authURL;
            }
        }
    }, []);

    useEffect(() => {
        if (token) {
            // Fetch user profile information using the access token
            axios
                .get('https://api.spotify.com/v1/me', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                })
                .then((response) => {
                    setUserProfile(response.data);
                })
                .catch((error) => {
                    console.error('Error fetching user profile:', error);
                });
        }
    }, [token]);

    return (
        <div>
            {userProfile ? (
                <div>
                    <h1>Welcome, {userProfile.display_name}!</h1>
                    <p>Email: {userProfile.email}</p>
                    <p>Spotify ID: {userProfile.id}</p>
                    {/* Display other user profile information as needed */}
                </div>
            ) : (
                <p>Loading user profile...</p>
            )}
        </div>
    );
};

export default SpotifyAuth;
