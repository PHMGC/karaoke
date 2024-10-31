import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Correção na importação
import { FaSearch } from 'react-icons/fa'; // Ícone de lupa
import Carousel from './Carousel';

// this file is responsible for the first page of the app, where the user inputs a YT url.

function HomePage() {

    // Variáveis auxiliares
    const [url, setUrl] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const videosNoBD = 3; // Recebe do DB o número de vídeos salvos.

    // Função de validação para checar se é um URL válido do YouTube
    const isValidYouTubeUrl = (url) => {
        const regex = /^(https?:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$/;
        return regex.test(url);
    };

    // Função para lidar com o envio do formulário  
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isValidYouTubeUrl(url)) {
            setError('Por favor, insira um link válido do YouTube.');
            return;
        }
        try {
            setError(''); // Remove qualquer mensagem de erro anterior
            navigate('/video', { state: { url } }); // Redireciona para a segunda página
        } catch (err) {
            setError('Erro ao conectar com o servidor.');
        }
    };

    return (
        <div className="min-h-screen flex flex-col font-jetbrains">

            {/* HEADER */}
            <header className="p-4 flex items-center">
                <img src="/icone.png" alt="Microphone" className="h-8 w-8 mr-2" />
                <h1 className="text-2xl font-bold">FeudoKe</h1> {/* Título do site */}
            </header>

            <div className={`flex ${videosNoBD > 2 ? 'flex-grow-[5] items-end' : 'flex-grow items-center'} justify-center pb-6 mt-[-10%]`}>
                <div className="w-1/2 max-w-lg">
                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            placeholder="video URL"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md outline-none text-black"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                        />
                        <button type="submit" className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 cursor-pointer">
                            <FaSearch />
                        </button>
                    </form>

                    {/* Exibir mensagem de erro */}
                    <div className="min-h-[1.5rem] mt-2">
                        {error.length > 1 && <p className="text-red-500 text-sm">{error}</p>}
                    </div>
                </div>
            </div>

            {(videosNoBD >= 2) && <div className="flex-grow-[1] flex justify-center items-center p-12">
                <Carousel />
            </div>}

            <footer className='flex items-center justify-center pb-2'>
                <span className="text-sm">© {new Date().getFullYear()} | Gustavo Ribeiro & Pedro Cortez</span>
            </footer>
        </div>
    );
}

export default HomePage;