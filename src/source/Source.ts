export interface Source {
    fetchData(): Promise<string[]>;
}
