// Client-to-server messages
export abstract class ClientToServerMessage {
    static readonly wrapperTypeName: string;
}

export class FreeMessage extends ClientToServerMessage {
    lockId: string;
    clientId: string;
    static readonly wrapperTypeName = "FreeMessage";
}

export class TryMessage extends ClientToServerMessage {
    lockId: string;
    clientId: string;
    static readonly wrapperTypeName = "TryMessage";
}

export class CreateParagraphSessionMessage extends ClientToServerMessage {
    sessionId: string;
    clientId: string;
    static readonly wrapperTypeName = "CreateParagraphSessionMessage";
}

export class UpdateParagraphSessionMessage extends ClientToServerMessage {
    sessionId: string;
    paragraphId: string;
    content: string;
    clientId: string;
    static readonly wrapperTypeName = "UpdateParagraphSessionMessage";
}

export class DeleteParagraphSessionMessage extends ClientToServerMessage {
    sessionId: string;
    paragraphId: string;
    clientId: string;
    static readonly wrapperTypeName = "DeleteParagraphSessionMessage";
}

export function send(ws: WebSocket, msg: ClientToServerMessage) {
    ws.send(JSON.stringify({
        "@inner": {
            "@type": (msg.constructor as typeof ClientToServerMessage).wrapperTypeName,
            "@content": msg,
        }
    }));
}

// Server-to-client messages
export interface ParagraphGoneSessionMessage {
    sessionId: string;
    paragraphId: string;
    clientId: string;
    deletedBy: string;
}

export interface InitMessage {
    lockId: string;
    clientId: string;
    lockedBy: string | null;
}

export interface ReadyMessage {
    lockId: string;
    clientId: string;
}

export interface BusyMessage {
    lockId: string;
    clientId: string;
    lockedBy: string;
}

export interface FreedMessage {
    lockId: string;
    clientId: string;
}

export interface InitSessionMessage {
    sessionId: string;
    clientId: string;
}

export interface UpdatedParagraphSessionMesssage {
    sessionId: string;
    paragraphId: string;
    content: string;
    clientId: string;
    updatedBy: string;
}

export type ServerToClientMessage =
    ParagraphGoneSessionMessage
    | InitMessage
    | ReadyMessage
    | BusyMessage
    | FreedMessage
    | InitSessionMessage
    | UpdatedParagraphSessionMesssage;

export interface ServerToClientMessageWrapper {
    "@inner": { "@type": string; "@content": ServerToClientMessage };
}

export interface ServerToClientMessageHandlerSet {
    sessionInitHandler: (msg: InitSessionMessage) => void;
    lockInitSessionHandler: (msg: InitMessage) => void;
    lockReadyHandler: (msg: ReadyMessage) => void;
    lockBusyHandler: (msg: BusyMessage) => void;
    lockFreedHandler: (msg: FreedMessage) => void;
    paragraphGoneHandler: (msg: ParagraphGoneSessionMessage) => void;
    paragraphUpdatedHandler: (msg: UpdatedParagraphSessionMesssage) => void;
}


export function dispatch(
    msg: ServerToClientMessageWrapper,
    handlers: ServerToClientMessageHandlerSet
): void {
    let inner = msg["@inner"];
    let msgType = inner["@type"];
    let content = inner["@content"];

    switch (msgType) {
        case "InitSessionMessage":
            handlers.sessionInitHandler(content as InitSessionMessage);
            break;
        case "InitMessage":
            handlers.lockInitSessionHandler(content as InitMessage);
            break;
        case "ReadyMessage":
            handlers.lockReadyHandler(content as ReadyMessage);
            break;
        case "BusyMessage":
            handlers.lockBusyHandler(content as BusyMessage);
            break;
        case "FreedMessage":
            handlers.lockFreedHandler(content as FreedMessage);
            break;
        case "ParagraphGoneSessionMessage":
            handlers.paragraphGoneHandler(content as ParagraphGoneSessionMessage);
            break;
        case "UpdatedParagraphSessionMesssage":
            handlers.paragraphUpdatedHandler(content as UpdatedParagraphSessionMesssage);
            break;
        default:
            throw new Error(`Unknown message type: ${msgType}`);
    }
}
