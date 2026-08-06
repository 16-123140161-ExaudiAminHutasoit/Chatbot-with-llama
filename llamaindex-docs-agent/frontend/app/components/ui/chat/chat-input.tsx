import { Button } from "../button";
import { Input } from "../input";
import { ChatHandler } from "./chat.interface";

export default function ChatInput(
  props: Pick<
    ChatHandler,
    "isLoading" | "handleSubmit" | "handleInputChange" | "input"
  >,
) {
  return (
    <form
      onSubmit={props.handleSubmit}
      className="flex w-full items-start justify-between gap-4 rounded-xl bg-white p-4 shadow-xl"
    >
      <Input
        autoFocus
        name="message"
        placeholder="Ketik pertanyaan seputar Sensus Ekonomi BPS..."
        className="flex-1"
        value={props.input}
        onChange={props.handleInputChange}
      />
      <Button type="submit" disabled={props.isLoading} className="bg-blue-600 hover:bg-blue-700 text-white font-medium">
        Kirim
      </Button>

    </form>
  );
}
