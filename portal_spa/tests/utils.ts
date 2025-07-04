import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import type React from "react";
import crypto from 'node:crypto';

export const renderWithRouter = (ui: React.ReactNode, { route = '/' } = {}) => {
    window.history.pushState({}, 'Test page', route);

    return {
        user: userEvent.setup(),
        ...render(ui, { wrapper: BrowserRouter }),
    };
};

export const generateJwt = (claims = {}) => {
    const header = {
        "alg": "HS256",
        "typ": "JWT"
    };
    const encodedHeaders = escape(btoa(JSON.stringify(header)));

    const expiresAfter = 90;
    claims = {
        email: 'test@example.com',
        role: 'maintainer',
        organizationSlugs: [],
        exp: Math.floor(Date.now() / 1000) + expiresAfter,
        ...claims,
    };
    const encodedPayload = escape(btoa(JSON.stringify(claims)));

    // create the signature part you have to take the encoded header,
    // the encoded payload, a secret, the algorithm specified in the header,
    // and sign that.
    const encodedSignature = escape(
        crypto.createHmac('sha256', '')
            .update(`${encodedHeaders}.${encodedPayload}`)
            .digest('base64')
    );

    return `${encodedHeaders}.${encodedPayload}.${encodedSignature}`;
};

const escape = (subject: string) => {
    return subject.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
};