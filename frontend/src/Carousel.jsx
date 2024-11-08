import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Slider from 'react-slick';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const Carousel = () => {

    const navigate = useNavigate();
    const [carouselData, setCarouselData] = useState(null);
    const [carouselLoading, setCarouselLoading] = useState(true);
    const [dbVideos, setDbVideos] = useState(1);
    const [dragging, setDragging] = useState(false);



    // functions to verify if the user is sliding or clicking

    const handleMouseDown = () => {
        setDragging(false); // Reset the state to ensure drag detection starts fresh
      };
    
      const handleMouseMove = () => {
        setDragging(true); // If the mouse moves, set dragging to true
      };
    
      const handleMouseUp = async (id) => {
        if (!dragging ) {
            navigate(`/video`);
        }
      };

    // Carousel DB request
    useEffect(() => {

        const fetchCarouselData = async () => {
            console.log("inciou")
            try {
                const response = await fetch('api/carousel');
                if (!response.ok) {
                    console.error("Erro da requisição");
                    throw new Error('Erro na requisição');
                }
                const result = await response.json();
                setCarouselData(result);
                setDbVideos(result.length);

            } catch (error) {
                console.error('Erro ao buscar informações do carrossel:', error);
            } finally {
                setCarouselLoading(false);
            }
        };
        fetchCarouselData();
    }, []);

    const showDots = (Math.ceil(dbVideos / 5) <= 5) ? true : false;
    var settings = {
        dots: showDots,
        infinite: true,
        speed: 2000,
        slidesToShow: (Math.ceil(dbVideos / 5)) >= 1 ? 5 : dbVideos,
        slidesToScroll: 5,
        initialSlide: 0,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3,
                    infinite: true,
                    dots: false
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2,
                    initialSlide: 2,
                    dots: false
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    dots: false
                }
            }
        ]
    };

    const items = Array.from({ length: 10 }, (_, index) => ({
        id: index + 1,
        thumbnail: 'https://img.youtube.com/vi/Qz52N7gsths/maxresdefault.jpg',
        title: '',
        subTitle: '',
    }));

    const sliderItems = carouselData && dbVideos >= 10 ? carouselData : items;

    return (
        <div className="w-full mx-auto">
            {carouselLoading  ? 
            <Slider {...settings}>
                {items.map((item) => (
                    <div key={item.id} className="flex flex-col items-center p-4 hover:cursor-pointer outline-none">
                        <div className="w-full aspect-video">
                            <img src={item.thumbnail} alt={item.title} className="w-full h-full object-cover rounded-md" />
                        </div>
                        <p className="text-black text-[11px] md:text-[13px] xl:text-[16px] font-bold text-center">{item.title}</p>
                        <p className="text-gray-800 text-[10px] md:text-[13px] xl:text-[14px] text-center">{item.subTitle}</p>
                    </div>
                ))}
            </Slider> 
            : 
            <Slider {...settings}>
                {sliderItems.map((item) => (
                    <div onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={() => handleMouseUp(item.uid)}
                     key={item.uid} className="flex flex-col items-center p-4 hover:cursor-pointer outline-none">
                        <div className="w-full aspect-video">
                            <img src={item.thumbnail} alt={item.title} className="w-full h-full object-cover rounded-md" />
                        </div>
                        <p className="text-black text-[11px] md:text-[13px] xl:text-[16px] font-bold  text-center">{item.title}</p>
                        <p className="text-gray-800 text-[10px] md:text-[13px] xl:text-[14px]  text-center">{item.subTitle}</p>
                    </div>
                ))}
            </Slider>
            }
        </div>
    );
};

export default Carousel;