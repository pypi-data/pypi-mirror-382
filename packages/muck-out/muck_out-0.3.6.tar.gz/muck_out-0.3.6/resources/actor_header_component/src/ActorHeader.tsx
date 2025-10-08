import "./ActorHeader.css";
import unknown from "./unknown.png";

import type { ActorHeaderInfo } from "@cattle-grid/muck-out-types/actor-header-info";

type ActorHeaderProps = {
  actorInfo: ActorHeaderInfo;
};

function transformIdentifier(identifier: string): string {
  return identifier.replace("acct:", "@");
}

function ActorHeaderName({ actorInfo }: ActorHeaderProps) {
  const name = actorInfo.name || "- unknown -";

  if (actorInfo.htmlUrl) {
    return (
      <div className="actor-header__name">
        <a href={actorInfo.htmlUrl}>{name}</a>
      </div>
    );
  }

  return <div className="actor-header__name">{name}</div>;
}

function ActorHeaderIdentifier({ actorInfo }: ActorHeaderProps) {
  return (
    <div className="actor-header__identifier">
      <a href={actorInfo.id}>{transformIdentifier(actorInfo.identifier)}</a>
    </div>
  );
}

function ActorHeader({ actorInfo }: ActorHeaderProps) {
  const avatar = actorInfo.avatarUrl || unknown;
  return (
    <header className="actor-header">
      <img src={avatar} className="actor-header__avatar" />
      <span>
        <ActorHeaderName actorInfo={actorInfo} />
        <ActorHeaderIdentifier actorInfo={actorInfo} />
      </span>
    </header>
  );
}

export default ActorHeader;
