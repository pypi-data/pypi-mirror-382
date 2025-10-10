import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import ActorHeader from "./ActorHeader";

const actor = {
  id: "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
  avatarUrl: "https://dev.bovine.social/assets/bull-horns.png",
  name: "The kitty",
  identifier: "acct:kitty@abel",
  htmlUrl: "http://abel/@kitty",
};

const noAvatar = { ...actor, avatarUrl: null };
const noName = { ...actor, name: null };

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <h3>Default</h3>
    <ActorHeader actorInfo={actor} />
    <h3>No avatar</h3>
    <ActorHeader actorInfo={noAvatar} />
    <h3>No name</h3>
    <ActorHeader actorInfo={noName} />
  </StrictMode>,
);
