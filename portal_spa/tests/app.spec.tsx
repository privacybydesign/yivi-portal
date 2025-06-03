import { it } from 'vitest';

import App from "@/App";
import { renderWithRouter } from "tests/utils";

it("should render app", () => {
    renderWithRouter(<App />);
});