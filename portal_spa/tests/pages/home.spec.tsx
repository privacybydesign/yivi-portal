import { expect, it } from "vitest";
import HomePage from "@/pages/HomePage";
import { renderWithRouter } from "tests/utils";
import { screen } from "@testing-library/dom";

it('renders the homepage', () => {
    renderWithRouter(<HomePage />);
    expect(screen.getByText(/Welcome to the Yivi Portal/)).toBeInTheDocument();
});