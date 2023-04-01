export class Lock {
    lockId: string;
    lockedBy: string | null;
    meTrying: boolean;
}