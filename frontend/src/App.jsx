import { useState, useEffect } from 'react'
import ContactList from './ContactList'
import './App.css'
import ContactForm from './ContactForm'

function App() {

    const [contacts, setContacts] = useState([])

    useEffect(() => {
        fetchContacts()
    }, [])

    const fetchContacts = async () => {
        const reponse = await fetch("http://127.0.0.1:5000/contacts")
        const data = await reponse.json()
        setContacts(data.contacts)
        console.log(data.contacts)
    }

    return (<>
        <ContactList contacts={contacts} />
        <ContactForm />
    </>)
}

export default App
