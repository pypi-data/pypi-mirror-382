import { create } from "zustand";

const inputs = (set, get) => ({
  inputs: [
    { id: "1", name: "Insta360", isSelected: true },
    { id: "2", name: "Go Pro 1", isSelected: false },
    { id: "3", name: "Go Pro 2", isSelected: false },
    { id: "4", name: "Go Pro 3", isSelected: false },
    { id: "5", name: "Go Pro 4", isSelected: false },
    { id: "6", name: "Go Pro 5", isSelected: false },
    { id: "7", name: "Go Pro 6", isSelected: false },
    { id: "8", name: "Go Pro 7", isSelected: false },
  ],

  addInput: ({ id, name, isSelected }) => {
    set((state) => ({
      inputs: [...state.inputs, { id, name, isSelected }],
    }));
  },

  removeInput: (id) => {
    set((state) => ({
      inputs: state.inputs.filter((input) => input.id !== id),
    }));
  },

  selectInput: (id) => {
    set((state) => ({
      inputs: state.inputs.map((input) =>
        input.id === id ? { ...input, isSelected: true } : input
      ),
    }));
  },

  deselectInput: (id) => {
    set((state) => ({
      inputs: state.inputs.map((input) =>
        input.id === id ? { ...input, isSelected: false } : input
      ),
    }));
  },

  toggleInputSelection: (id) => {
    const { inputs, selectInput, deselectInput } = get();
    const currentlySelected = inputs.find((input) => input.isSelected);
    if (currentlySelected) {
      deselectInput(currentlySelected.id);
    }
    selectInput(id);
  },

  getSelectedInput: () => {
    const { inputs } = get();
    const selectedInput = inputs.find((input) => input.isSelected);

    if (selectedInput) {
      return selectedInput;
    } else if (inputs.length > 0) {
      return inputs[0];
    } else {
      return null;
    }
  },
});

const useInputsStore = create(inputs);

export default useInputsStore;
