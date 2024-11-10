import React, { useState} from 'react';
import { useNavigate } from 'react-router-dom'; // Correção na importação
import { FaSearch } from 'react-icons/fa'; // Ícone de lupa
import Carousel from './Carousel';

// this file is responsible for the first page of the app, where the user inputs a YT prompt.

function HomePage() {

    // Variáveis auxiliares
    const [prompt, setPrompt] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    // Função de validação para checar se é um URL válido do YouTube
    const isValidYouTubeUrl = (prompt) => {
        const regex = /^(https?:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$/;
        return regex.test(prompt);
    };

    // Função para lidar com o envio do formulário  
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(''); // Remove qualquer mensagem de erro anterior
    
        try {
            if (!isValidYouTubeUrl(prompt)) {
                navigate('/videos', { state: { prompt } }); // Redireciona para '/videos' se o URL for inválido
            } else {
                navigate('/video', { state: { prompt } }); // Redireciona para '/video' se o URL for válido
            }
        } catch (err) {
            setError('Erro ao conectar com o servidor.');
        }
    };
    

    return (
        <div className="min-h-screen flex flex-col font-jetbrains">

            {/* HEADER */}
            <header className="p-4 flex items-center z-10">
                <img onClick={()=>navigate("/")} src="/icone.png" alt="Microphone" className="h-8 w-8 mr-2 hover:cursor-pointer" />
                <h1  onClick={()=>navigate("/")} className="text-2xl font-bold hover:cursor-pointer">KaraokeTube</h1> {/* Título do site */}
            </header>

            <div className={`flex ${'flex-grow-[5] items-end'} justify-center pb-6 mt-[-10%]`}>
                <div className="w-1/2 max-w-lg">
                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            placeholder="video URL"
                            className="w-full px-4 py-2 border border-gray-300 rounded-md outline-none text-black"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
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

            <div className="flex-grow-[1] flex flex-col justify-center items-center p-12">
                <p className='pb-4 text-center text-xl text-black'>Top 10</p>
                <Carousel />
            </div>

            <footer className='flex items-center justify-center pb-2'>
                <span className="text-sm">© {new Date().getFullYear()} | Gustavo Ribeiro & Pedro Cortez</span>
            </footer>
        </div>
    );
}

export default HomePage;