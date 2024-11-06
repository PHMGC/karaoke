import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Slider from 'react-slick';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const Carousel = () => {

    const navigate = useNavigate();
    const [carouselData, setCarouselData] = useState({});
    const [carouselLoading, setCarouselLoading] = useState(true);
    const [dbVideos, setDbVideos] = useState(10);
    const [dragging, setDragging] = useState(false);



    // functions to verify if the user is sliding or clicking

    const handleMouseDown = () => {
        setDragging(false); // Reset the state to ensure drag detection starts fresh
      };
    
      const handleMouseMove = () => {
        setDragging(true); // If the mouse moves, set dragging to true
      };
    
      const handleMouseUp = (id) => {
        if (!dragging && dbVideos >= 10) {
          navigate(`/api/video/karaoke/${id}`);
        }
      };

    // Carousel DB request
    useEffect(() => {
        const fetchCarouselData = async () => {
            try {
                const response = await fetch('api/carousel')
                if(!response.ok){
                    throw new Error('Erro na requisição');
                }
                const result = await response.json();
                setCarouselData(result);
                console.log(result);
                setDbVideos(result.length)
                
            } catch (error) {
                console.error('Erro ao buscar informações do carrossel:', error);
            } finally {
                setCarouselLoading(false);
              }
        }; 
            fetchCarouselData();
        
    },[]);

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
        image: 'https://media-gig4-2.cdn.whatsapp.net/v/t61.24694-24/361179864_3607290972930022_2288009550893722469_n.jpg?ccb=11-4&oh=01_Q5AaIMlM7DIWdfvBxvYCJB4ZUTioPT1P1yk5GwLuelxOadLt&oe=67328156&_nc_sid=5e03e0&_nc_cat=105',
        title: `Pedron`,
        subTitle: 'Pedrito'
    }));

    const sliderItems = dbVideos >= 10 ? carouselData : items;

    return (
        <div className="w-full mx-auto">
            {carouselLoading ? 
            <Slider {...settings}>
                {items.map((item) => (
                    <div key={item.id} className="flex flex-col items-center p-4 hover:cursor-pointer outline-none">
                        <img src={item.image} alt={item.title} className="w-full h-auto object-cover rounded-md mb-2" />
                        <h2 className="text-black text-lg font-bold  text-center">{item.title}</h2>
                        <h3 className="text-gray-800 text-sm  text-center">{item.subTitle}</h3>
                    </div>
                ))}
            </Slider> 
            : 
            <Slider {...settings}>
                {sliderItems.map((item) => (
                    <div onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={() => handleMouseUp(item.uid)}
                     key={item.uid} className="flex flex-col items-center p-4 hover:cursor-pointer outline-none">
                        <img src={item.thumbnail} alt={item.title} className="w-full h-auto object-cover rounded-md mb-2" />
                        <h2 className="text-black text-lg font-bold  text-center">{item.title}</h2>
                        <h3 className="text-gray-800 text-sm  text-center">{item.subTitle}</h3>
                    </div>
                ))}
            </Slider>
            }
        </div>
    );
};

export default Carousel;