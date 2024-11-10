import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';




function SelectionPage() {

    const location = useLocation();
    const navigate = useNavigate();
    const { prompt } = location.state || {}; // recebe a url do video da rota /
    const [videosInfo, setVideosInfo] = useState(null);

    useEffect(() => {
        const fetchVideosInfo = async () => {
            try {
                const amount = 10;
                const response = await fetch('api/video/info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt, amount }),
                });
    
                const data = await response.json();
                console.log(data)
                const mappedData = data.map(item => ({
                    title: item.title,
                    thumbnail: item.thumbnail,
                    channel: item.channel,
                    duration: item.duration,
                }));
                
                setVideosInfo(mappedData);
            } catch (error) {
                console.error('Erro ao buscar informações do vídeo:', error);
            }
        };
        if (prompt) {
            fetchVideosInfo();
        }
    }, [prompt]);

    return(
        <div className="min-h-screen flex flex-col font-jetbrains">
            <header className="p-4 flex items-center z-10">
                <img onClick={()=>navigate("/")} src="/icone.png" alt="Microphone" className="h-8 w-8 mr-2 hover:cursor-pointer" />
                <h1 onClick={()=>navigate("/")} className="text-2xl font-bold hover:cursor-pointer">KaraokeTube</h1>
            </header>
        </div>
    );



}

export default SelectionPage;