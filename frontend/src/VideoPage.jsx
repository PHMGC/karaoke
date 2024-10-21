import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// this file is responsible for the second page of the app, 
// where the user starts the karaoke generation.

function VideoPage() {

    // variaveis auxiliares
    const location = useLocation();
    const navigate = useNavigate();
    const { url } = location.state || {}; // recebe a url do video da rota /
    const [videoInfo, setVideoInfo] = useState(null);
    const [isImageLoaded, setIsImageLoaded] = useState(false);
    const [loadingVideo, setLoadingVideo] = useState(false);
    const [progress, setProgress] = useState(0); // Progresso atual
    const [error, setError] = useState('');
    const eventSourceRef = useRef(null);
    const [videoGenerated, setVideoGenerated] = useState(false);
    const [videoUrl, setVideoUrl] = useState('');


    useEffect(() => {
        const fetchVideoInfo = async () => {
            try {
                const response = await fetch('/api/video/info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url }),
                });
                if (response.status != 200) {
                    console.error("error receiving video info:")
                    console.error(response)
                }
                const data = await response.json();
                setVideoInfo({
                    title: data.title,
                    thumbnail: data.thumbnail,
                    channel: data.channel,
                    duration: data.duration,
                });
            } catch (error) {
                console.error('Erro ao buscar informações do vídeo:', error);
            }
        };

        if (url) {
            fetchVideoInfo();
        }
    }, [url]);

    // inicia o processo de geração
    const handleGenerateKaraoke = async () => {
        setLoadingVideo(true);
        setError('');

        // essa parte prepara o front end para receber dados do back end
        try {
            //permite que o servidor envie atualizações em tempo real para o cliente
            const eventSource = new EventSource('/api/progress');
            eventSourceRef.current = eventSource;

            //é disparado sempre que o servidor envia dados para o cliente, armazenando o progresso;
            eventSource.onmessage = (event) => {
                setProgress(parseFloat(event.data));
                //console.log(`progress: ${progress}%`)

                if (progress >= 100) {
                    setVideoGenerated(true);
                    setLoadingVideo(false);
                    setVideoUrl('/api/video/final');
                    eventSource.close(); // Fechar conexão SSE
                }

            };
        } catch (error) {
            setError(error.message);
            setLoadingVideo(false);
        }
    };

    // retonar a home page
    const returnHomePage = async () => {
        eventSourceRef.current.close()
        navigate('/'); // voltar para a home page ao clicar no botao voltar
    };
    // ---------------------------------------------------------------------------------------------
    return (
        <div className="min-h-screen flex flex-col font-jetbrains">
            <header className="p-4 flex items-center">
                <img src="/icone.png" alt="Microphone" className="h-8 w-8 mr-2" />
                <h1 className="text-2xl font-bold">FeudoKe</h1>
            </header>

            {videoGenerated ? (
                <div className="flex-grow flex flex-col justify-center items-center">
                    <video
                        controls
                        className="w-full max-w-4xl h-auto rounded-lg"
                        src={videoUrl}
                        autoPlay
                    />

                    <button
                        className="mt-4 p-2 bg-gray-300 text-black rounded hover:bg-gray-400"
                        onClick={returnHomePage} // Retorna a home page
                    >
                        Voltar
                    </button>
                </div>
            ) : (
                <div className="flex-grow flex flex-col md:flex-row p-8 justify-center items-center mt-[-5%]">
                    <div className="flex-1 flex justify-center items-center mb-6 md:mb-0">
                        {videoInfo ? (
                            <img
                                src={videoInfo.thumbnail}
                                alt="Thumbnail do vídeo"
                                loading="lazy"
                                className={`w-full max-w-lg md:max-w-2xl h-auto rounded-lg shadow-lg object-cover transition-all duration-700 ease-in-out ${isImageLoaded ? 'blur-0 opacity-100' : 'blur-md opacity-50'
                                    }`}
                                onLoad={() => setIsImageLoaded(true)}
                            />
                        ) : (
                            <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
                        )}
                    </div>

                    {videoInfo && (
                        <div className="flex-1 flex flex-col justify-center items-center text-center">
                            <h1 className="text-3xl font-bold mb-4">{videoInfo.title}</h1>
                            <p className="text-lg mb-2">{videoInfo.channel}</p>
                            <p className="text-lg mb-2">Duração: {videoInfo.duration}</p>

                            <div className="mt-4 flex flex-col items-center w-full">
                                {!loadingVideo && !error && (
                                    <button
                                        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                        onClick={handleGenerateKaraoke}
                                        disabled={loadingVideo}
                                    >
                                        Iniciar Karaoke
                                    </button>
                                )}

                                {loadingVideo ? (
                                    progress < 100 ? (
                                        <div>
                                            <div className="w-full max-w-3xl bg-gray-200 mt-4 rounded-2xl h-5">
                                                <div
                                                    className="bg-blue-500 text-xs leading-none py-1 text-center rounded-2xl text-white h-full"
                                                    style={{ width: `${progress}%` }}
                                                >
                                                    {progress.toFixed(0)}%
                                                </div>
                                            </div>
                                            <div className="mt-4 text-lg font-bold text-center flex flex-col items-center gap-1">
                                                <p>Seu vídeo está sendo gerado, prepare-se para cantar 🎤</p>
                                                <p className='text-sm'>Essa etapa pode demorar alguns minutos</p>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="mt-4 text-lg font-bold text-center">
                                            <p>Seu vídeo foi gerado com sucesso! 🎉</p>
                                            <button onClick={() => { }} className="mt-2 bg-blue-500 text-white py-2 px-4 rounded">Baixar Vídeo</button>
                                        </div>
                                    )
                                ) : null}

                                <button
                                    className="mt-4 p-2 bg-gray-300 text-black rounded hover:bg-gray-400"
                                    onClick={returnHomePage}
                                >
                                    Voltar
                                </button>

                                {error && <p className="text-red-500 mt-2">{error}</p>}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default VideoPage;
