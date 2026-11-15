import React from "react";
import { Img, staticFile } from "remotion";
import { COLORS, FONTS, TEXT_SHADOW } from "../lib/theme";
import { easeOut, mix, prog } from "../lib/anim";

// Logo « Femmes de foi en affaires » : emblème doré vectorisé (potrace, net à toute
// taille) + nom recomposé proprement (l'original est rogné par le cercle du visuel).
export const Logo: React.FC<{
  frame: number;
  start: number;
  size?: number;
  showName?: boolean;
  medallion?: boolean;
}> = ({ frame, start, size = 300, showName = true, medallion = false }) => {
  const pe = prog(frame, start, 18, easeOut);
  const pn = prog(frame, start + 8, 16, easeOut);
  return (
    <div
      style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
    >
      <div
        style={{
          width: size * (medallion ? 1.32 : 1),
          height: size * (medallion ? 1.32 : 1),
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: medallion
            ? "radial-gradient(circle, rgba(34,9,16,0.94) 0%, rgba(26,7,12,0.9) 62%, rgba(26,7,12,0) 72%)"
            : undefined,
          opacity: medallion ? pe : 1,
        }}
      >
        <Img
          src={staticFile("brand/emblem_gold.svg")}
          style={{
            width: size,
            height: size,
            opacity: pe,
            transform: `scale(${mix(0.88, 1, pe)}) rotate(${mix(-8, 0, pe)}deg)`,
            filter: `drop-shadow(0 6px 22px rgba(10,3,5,0.55)) drop-shadow(0 0 30px rgba(235,201,143,${0.25 * pe}))`,
          }}
        />
      </div>
      {showName ? (
        <div
          style={{
            marginTop: size * (medallion ? 0.02 : 0.12),
            fontFamily: FONTS.sans,
            fontWeight: 500,
            fontSize: size * 0.165,
            letterSpacing: `${mix(0.45, 0.28, pn)}em`,
            paddingLeft: "0.28em",
            textTransform: "uppercase",
            color: COLORS.white,
            opacity: pn,
            textShadow: TEXT_SHADOW,
            whiteSpace: "nowrap",
          }}
        >
          Femmes de foi en affaires
        </div>
      ) : null}
    </div>
  );
};
