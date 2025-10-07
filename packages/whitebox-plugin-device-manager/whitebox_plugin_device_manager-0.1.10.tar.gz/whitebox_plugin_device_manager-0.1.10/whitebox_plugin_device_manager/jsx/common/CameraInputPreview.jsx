import { useEffect, useState } from "react";

const {
  importWhiteboxComponent,
  importWhiteboxStateStore,
  withStateStore,
} = Whitebox;

const WifiIcon = importWhiteboxComponent("icons.wifi");

const InputCard = ({ input, toggleInputSelection }) => {
  return (
    <>
      <div
        className="flex flex-col items-center gap-2 cursor-pointer"
        onClick={() => toggleInputSelection(input.id)}
      >
        <div
          className={`h-24 w-24 bg-gray-5 rounded-3xl ${
            input.isSelected ? "border-2 border-gray-1" : ""
          }`}
        >
          <div className="w-full flex justify-end p-2">
            <WifiIcon />
          </div>
        </div>
        <p className="text-md">{input.name}</p>
      </div>
    </>
  );
};

const PreviewWindow = ({ selectedInputName }) => {
  return (
    <>
      <div className="w-full h-72 bg-gray-5 rounded-3xl flex items-center justify-center text-2xl">
        {selectedInputName || "NO INPUTS"}
      </div>
    </>
  );
};

const CameraInputPreviewToWrap = () => {
  const [inputs, setInputs] = useState([]);
  const [selectedInputName, setSelectedInputName] = useState("");
  const [toggleInputSelection, setToggleInputSelection] = useState(
    () => () => {}
  );

  useEffect(() => {
    let unsub;
    let useInputsStore;
    let updateFromStore = () => {};

    async function loadStores() {
      useInputsStore = importWhiteboxStateStore("flight.inputs");
      setInputs(useInputsStore.getState().inputs);
      setToggleInputSelection(
        () => useInputsStore.getState().toggleInputSelection
      );
      setSelectedInputName(
        useInputsStore.getState().getSelectedInput?.()?.name ?? ""
      );

      // Subscribe to store changes if available
      if (useInputsStore.subscribe) {
        updateFromStore = () => {
          setInputs(useInputsStore.getState().inputs);
          setSelectedInputName(
            useInputsStore.getState().getSelectedInput?.()?.name ?? ""
          );
        };
        unsub = useInputsStore.subscribe(updateFromStore);
      }
    }

    loadStores();

    return () => {
      if (unsub) unsub();
    };
  }, []);

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex-1 mb-4">
        <PreviewWindow selectedInputName={selectedInputName} />
      </div>
      <div className="flex flex-row gap-4 overflow-x-auto py-4">
        {inputs.map((input, index) => (
          <InputCard
            key={index}
            input={input}
            toggleInputSelection={toggleInputSelection}
          />
        ))}
      </div>
    </div>
  );
};

const CameraInputPreview = withStateStore(
    CameraInputPreviewToWrap,
    ["flight.inputs"],
)

export default CameraInputPreview;
export { CameraInputPreview };
