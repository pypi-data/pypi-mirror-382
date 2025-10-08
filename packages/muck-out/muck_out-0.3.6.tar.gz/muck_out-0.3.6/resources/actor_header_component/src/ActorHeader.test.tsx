import { expect, test } from "vitest";
import { render } from "vitest-browser-react";

import ActorHeader from "./ActorHeader";

test("renders actor", async () => {
  const actor = {
    id: "http://abel/actor/AFKb0cQunSBv1fC7sWbQYg",
    avatarUrl: "https://dev.bovine.social/assets/bull-horns.png",
    name: "The kitty",
    identifier: "acct:kitty@abel",
    htmlUrl: "http://abel/@kitty",
  };

  const { getByText, getByRole } = render(<ActorHeader actorInfo={actor} />);

  expect(getByText("the kitty")).toBeInTheDocument();
  expect(getByText("@kitty@abel")).toBeInTheDocument();

  const avatar = getByRole("img");

  expect(avatar).toBeInTheDocument();
  expect(avatar.element().getAttribute("src")).toBe(actor.avatarUrl);
});
