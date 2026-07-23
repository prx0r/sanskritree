namespace Sanskritree

structure InterpretationContext where
  Entity : Type
  Power : Entity → Prop
  Manifest : Entity → Prop
  DependsOn : Entity → Entity → Prop

end Sanskritree
