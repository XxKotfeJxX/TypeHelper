async function createDebugTextLayers(blocks) {
  const core = require("photoshop").core;
  const batchPlay = require("photoshop").action.batchPlay;
  const app = require("photoshop").app;

  const doc = app.activeDocument;
  const docHeight = doc.height; // <-- у px, Photoshop сам приведе

  await core.executeAsModal(
    async () => {
      // Створити групу
      const makeGroup = await batchPlay(
        [
          {
            _obj: "make",
            _target: [{ _ref: "layerSection" }],
            name: "TypeHelper Debug",
          },
        ],
        { synchronousExecution: true }
      );

      const groupID = makeGroup[0]._target[0]._id;

      for (const b of blocks) {
        const [x, y, w, h] = b.bbox.map(Number);
        const cx = Math.round(x + w / 2);
        const cyRaw = Math.round(y + h / 2);

        // Adobe UXP BUG FIX → координати >8192 ламають NAPI
        const cy = Math.min(cyRaw, 8192);

        const name = `object #${b.id}`;

        console.log("→ CREATE", name, cx, cyRaw, "(used:", cy, ")");

        // 1) створити текстовий шар
        await batchPlay(
          [
            {
              _obj: "make",
              _target: [{ _ref: "layer" }],
              using: {
                _obj: "textLayer",
                name: name,
                textKey: name,
                textStyleRange: [
                  {
                    _obj: "textStyleRange",
                    from: 0,
                    to: name.length,
                    textStyle: {
                      _obj: "textStyle",
                      size: { _unit: "pointsUnit", _value: 20 },
                      color: {
                        _obj: "RGBColor",
                        red: 255,
                        green: 50,
                        blue: 50,
                      },
                    },
                  },
                ],
                textClickPoint: {
                  _obj: "paint",
                  horizontal: { _unit: "pixelsUnit", _value: cx },
                  vertical: { _unit: "pixelsUnit", _value: cy },
                },
              },
            },
          ],
          { synchronousExecution: true }
        );

        // 2) перемістити шар у групу
        await batchPlay(
          [
            {
              _obj: "move",
              _target: [
                { _ref: "layer", _enum: "ordinal", _value: "targetEnum" },
              ],
              to: { _ref: "layerSection", _id: groupID },
            },
          ],
          { synchronousExecution: true }
        );
      }
    },
    { commandName: "TypeHelper Debug Insert" }
  );

  console.log("✔ DEBUG TEXT CREATED");
}
