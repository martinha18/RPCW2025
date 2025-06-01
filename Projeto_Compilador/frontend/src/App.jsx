import React from 'react';
import {SocketProvider} from './SocketContext.jsx';
import {BrowserRouter, Route, Routes} from "react-router-dom";
import {Admin} from "./pages/Admin.jsx";
import Explorer from "./pages/Explorer.jsx";
import {Home} from "./pages/Home.jsx";

const App = () => (
    <SocketProvider>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/admin/:ont" element={<Explorer />} />
            </Routes>
        </BrowserRouter>
    </SocketProvider>
);

export default App;
