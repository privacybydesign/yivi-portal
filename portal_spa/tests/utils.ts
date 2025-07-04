import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import type React from "react";

export const renderWithRouter = (ui: React.ReactNode, { route = '/' } = {}) => {
    window.history.pushState({}, 'Test page', route);

    return {
        user: userEvent.setup(),
        ...render(ui, { wrapper: BrowserRouter }),
    };
};