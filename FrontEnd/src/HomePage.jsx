import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Correção na importação
import { FaSearch } from 'react-icons/fa'; // Ícone de lupa

// this file is responsible for the first page of the app, where the user inputs a YT url.

function HomePage() {

    // Variáveis auxiliares
    const [url, setUrl] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate(); 
  
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

        <div className="flex-grow flex justify-center items-center mt-[-10%]">
          <div className="w-1/2 max-w-lg">
            <form onSubmit={handleSubmit} className="relative">
              <input
                type="text"
                placeholder="video URL"
                className="w-full px-4 py-2 border border-gray-300 rounded-md outline-none"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <button type="submit" className="absolute right-3 top-3 text-gray-400 hover:text-gray-600 cursor-pointer">
                <FaSearch />
              </button>
            </form>
  
            {/* Exibir mensagem de erro abaixo do formulário */}
            {error.length > 1 && <p className="text-red-500 mt-2 text-sm">{error}</p>}
          </div>
        </div>
      </div>
    );
}

export default HomePage;
