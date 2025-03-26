interface PaginationResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Organization[];
}