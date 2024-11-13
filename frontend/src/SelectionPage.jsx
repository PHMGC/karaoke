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
                const mappedData = data.map(item => ({
                    uid: item.uid,
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

    const handleVideoClick = (id) => {
        const prompt = 'https://www.youtube.com/watch?v=' + id;
        navigate('/video', { state: { prompt } });
    };

    return(
        <div className="min-h-screen flex flex-col font-jetbrains">
            <header className="p-4 flex items-center z-10">
                <img onClick={()=>navigate("/")} src="/icone.png" alt="Microphone" className="h-8 w-8 mr-2 hover:cursor-pointer" />
                <h1 onClick={()=>navigate("/")} className="text-2xl font-bold hover:cursor-pointer">KaraokeTube</h1>
            </header>
            <div>
            <div>
            </div>
            <div className="grid grid-cols-1 gap-4 p-4 px-10 md:px-20 lg:px-44">
                {videosInfo && videosInfo.length > 0 ? (
                    videosInfo.map((item, index) => (
                        <div 
                            key={index} 
                            className="hover:cursor-pointer border border-gray-300 p-4 gap-8 rounded-lg flex flex-col lg:flex-row"
                            onClick={() => handleVideoClick(item.uid)}
                        >
                        <div className="mx-auto justify-center items-center flex flex-2 max-w-[300px] lg:max-w-[400px] aspect-video">
                            <img
                                src={item.thumbnail}
                                alt={item.title}
                                className=" w-full h-full object-cover rounded-md"
                            />
                        </div>
                        <div className='flex flex-1  flex-col items-center justify-center gap-4 p-4'>
                            <p className="flex text-gray-800 font-bold text-[10px] md:text-[13px] xl:text-[18px] text-center">
                                {item.title}
                            </p>
                            <p className="flex text-gray-800 text-[10px] md:text-[13px] xl:text-[16px] text-center">
                                {item.channel}
                            </p>
                            <p className="flex text-gray-800 text-[10px] md:text-[13px] xl:text-[15px] text-center">
                                {item.duration}
                            </p>
                        </div>
                    </div>
                    ))
                ) : (
                    <div className='flex flex-col gap-8 items-center justify-start w-full h-screen pt-80'>  
                        <p className='flex text-center'>Searching Videos</p> 
                        <div className="flex animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>   
                    </div>
                    
                    
                )}
            </div>
            <div className='p-4 flex items-center justify-center'>
                <button className="text-[10px] sm:text-[12px] lg:text-[16px] mt-4 p-2
                            bg-gray-300 text-black rounded hover:bg-gray-400"
                            onClick={()=> {navigate("/")} } >
                    Voltar        
                            
                </button>
            </div>
            </div>
        </div>
    );



}

export default SelectionPage;