export interface UserIn {
    firstname: string;
    lastname:  string;
    nickname?: string;
    email:     string;
}
  
export interface UserOut extends UserIn {
    id: number;
}
  