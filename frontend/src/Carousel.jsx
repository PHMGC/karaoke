import React, { useState } from 'react';
import Slider from 'react-slick';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const videosNoBD = 3

const Carousel = () => {

    const showDots = (Math.ceil(videosNoBD / 5) <= 5) ? true : false;
    var settings = {
        dots: showDots,
        infinite: true,
        speed: 2000,
        slidesToShow: (Math.ceil(videosNoBD / 5)) >= 1 ? 5 : videosNoBD,
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

    const items = Array.from({ length: videosNoBD }, (_, index) => ({
        id: index + 1,
        image: 'https://img.youtube.com/vi/5NueopkCwJQ/maxresdefault.jpg',
        title: `Title ${index + 1}`
    }));

    return (
        <div className="w-full mx-auto">
            <Slider {...settings}>
                {items.map((item) => (
                    <div key={item.id} className="flex flex-col items-center p-4 hover:cursor-pointer outline-none">
                        <img src={item.image} alt={item.title} className="w-full h-auto object-cover rounded-md mb-2" />
                        <h2 className="text-black text-lg font-bold  text-center">{item.title}</h2>
                        <h3 className="text-gray-800 text-sm  text-center">{item.title}</h3>
                    </div>
                ))}
            </Slider>
        </div>
    );
};

export default Carousel;
