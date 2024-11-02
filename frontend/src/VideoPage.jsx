import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// this file is responsible for the second page of the app, 
// where the user starts the karaoke generation.

function VideoPage() {

    // variaveis auxiliares
    const location = useLocation();
    const navigate = useNavigate();
    const { url } = location.state || {}; // recebe a url do video da rota /
    const [uid, setUid] = useState('');
    const [videoPath, setVideoPath] = useState('');
    const [videoInfo, setVideoInfo] = useState(null);
    const [isImageLoaded, setIsImageLoaded] = useState(false);
    const [loadingVideo, setLoadingVideo] = useState(false);
    const [progress, setProgress] = useState(0); // Progresso atual
    const [error, setError] = useState('');
    const eventSourceRef = useRef(null);
    const [videoGenerated, setVideoGenerated] = useState(false);
    const [startedProcessing, setStartedProcessing] = useState(false); // Para controlar quando o processo de karaoke começou



    // essa parte envia uma requisição para a api no backend, do tipo POST (envia a url),
    // e armazena na variável VideoInfo as informaçoes do video.
    useEffect(() => {
        const fetchVideoInfo = async () => {
            try {
                const response = await fetch('api/video/info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url }),
                });

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
        setStartedProcessing(true);
        setProgress(0);
        setError('');
        try {
            var postData;
            // Solicita ao backend que inicie o processamento do vídeo
            const postResponse = await fetch('api/video/karaoke', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            if (!postResponse.ok) {
                throw new Error('Erro ao processar o vídeo.');
            }
            else {
                postData = await postResponse.json();
                setUid(postData);
            }
            if (postData.videoPath == null) {
                console.log("postData:");
                console.log(postData);
                // Cria a conexão SSE para receber atualizações de progresso em tempo real
                console.log(`Connecting to EventSource(api/video/karaoke/${postData.uid})`);
                const eventSource = new EventSource(`api/video/karaoke/${postData.uid}`);
                eventSourceRef.current = eventSource;
                eventSource.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    console.log("data:");
                    console.log(data);
                    const { progress, videoPath, error } = data;
                    setVideoPath(videoPath);

                    if (error) {
                        setError(error);
                        eventSource.close();
                        return;
                    }

                    if (typeof progress === 'number' && progress >= 0 && progress <= 100) {
                        setProgress(progress); // Atualiza o estado da barra de progresso

                        // Fecha a conexão SSE e configura o vídeo ao atingir 100% de progresso
                        if (progress === 100) {
                            setVideoGenerated(true);
                            eventSource.close();
                            setLoadingVideo(false);
                        }
                    }
                };
                eventSource.onerror = (event) => {
                    console.error('EventSource failed:', event);
                    eventSource.close(); // Close on error to prevent leaks
                    setLoadingVideo(false);
                };

            }
            else {
                setVideoPath(postData.videoPath);
                setVideoGenerated(true);
            }
        } catch (error) {
            setError(error.message);
            setLoadingVideo(false);
        }
    };

    // Essa parte tambem deleta os video e pode ser ignorada
    // pois faremos tudo no backend de forma mais simples
    // manter a funcionalidade do botao
    // ---------------------------------------------------------------------------------------------
    const handleDeleteVideo = async () => {
        /*try {
          // Chamada para deletar o vídeo ao clicar no botão "Voltar"
          const response = await fetch('api/video/delete', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          if (response.ok) {
            //console.log('Vídeo deletado');
          }
        } catch (error) {
          console.error('Erro ao deletar o vídeo:', error);
        }*/
        navigate('/'); // voltar para a pagina anterior ao clicar no botao voltar
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
                        src={videoPath}
                        autoPlay
                    />

                    <button
                        className="mt-4 p-2 bg-gray-300 text-black rounded hover:bg-gray-400"
                        onClick={handleDeleteVideo} // Retorna a pagina anterior
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

                                {loadingVideo && progress < 100 && (
                                    <div className="w-full max-w-3xl bg-gray-200 mt-4 rounded-2xl h-5">
                                        <div
                                            className="bg-blue-500 text-xs leading-none py-1 text-center rounded-2xl text-white h-full"
                                            style={{ width: `${progress}%` }}
                                        >
                                            {progress.toFixed(0)}%
                                        </div>
                                    </div>
                                )}

                                {startedProcessing && progress < 100 && progress < 100 ? (
                                    <div className="mt-4 text-lg font-bold text-center flex flex-col items-center gap-1">
                                        <p>Seu vídeo está sendo gerado, prepare-se para cantar 🎤</p>
                                        <p className='text-sm'>Essa etapa pode demorar alguns minutos</p>
                                    </div>
                                ) : (progress === 100 && !videoGenerated) ? (
                                    <div className="mt-4 flex flex-col items-center">
                                        <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mt-4"></div>
                                        <p className='mt-2 text-lg'>Carregando o vídeo...</p>
                                    </div>
                                ) : null}

                                <button
                                    className="mt-4 p-2 bg-gray-300 text-black rounded hover:bg-gray-400"
                                    onClick={handleDeleteVideo}
                                >
                                    Voltar
                                </button>

                                {error && <p className="text-red-500 mt-2">{error}</p>}
                            </div>
                        </div>
                    )}
                </div>
            )}
            <footer className='flex items-center justify-center pb-2'>
                <span className=" text-[.78rem] sm:text-sm">© {new Date().getFullYear()} | Gustavo Ribeiro & Pedro Cortez</span>
            </footer>
        </div>
    );
}

export default VideoPage;