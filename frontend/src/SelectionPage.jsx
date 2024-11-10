import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';




function SelectionPage() {

    const location = useLocation();
    const navigate = useNavigate();
    const { url } = location.state || {}; // recebe a url do video da rota /

    return(

        <div>
            Hello World
        </div>
    );



}

export default SelectionPage;