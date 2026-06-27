// NewUI Demo Entry Point
// This file allows you to preview the new UI design

import React from 'react';
import ReactDOM from 'react-dom/client';
import NewUI from './NewUI';
import './NewUI.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <NewUI />
  </React.StrictMode>
);
