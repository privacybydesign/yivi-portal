import { UUID } from 'crypto';

export interface Maintainer {
    id: string;
    email: string;
    role: string;
    organization: UUID;
    // first_name: string;
    // last_name: string;
}