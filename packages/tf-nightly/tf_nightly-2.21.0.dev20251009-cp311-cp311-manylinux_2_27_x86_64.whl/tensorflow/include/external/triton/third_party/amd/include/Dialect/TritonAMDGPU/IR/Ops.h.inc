/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Declarations                                                            *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: TritonAMDGPUOps.td                                                   *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace triton {
namespace amdgpu {
/// Atomic CAS op which does compare-exchange to a scalar base pointer and a tensor offset
/// AMD Buffer Atomic CAS operation. Buffer atomics are similar to normal atomics, but access global memory via a
///         scalar base pointer and a tensor of offsets instead of a tensor of pointers.
///         Similar to TT_AtomicCASOp: Buffer atomic CAS op loads data at $ptr, and stores $val to $ptr atomically if value at $ptr equals $cmp, with
///         the specified memory semantics and scope. Atomic CAS ops return the pre-op value if used, otherwise the value is implicitly dropped.
///         Stride is the distance between the beginning of contiguous memory chunks. When performing a CAS, the `stride` is
///         the address difference between the first elements of each row in bytes. Compiler tries to obtain the `stride`
///         when it converts to the buffer ops because it is important for optimizing the cache memory access.
class BufferAtomicCASOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Atomic RMW op which reads, modifies, and writes to a scalar base pointer and a tensor offset
/// AMD Buffer atomic RMW operation. Buffer atomics are similar to normal atomics, but access global memory via a
///         scalar base pointer and a tensor of offsets instead of a tensor of pointers.
///         Similar to other buffer ops, the `mask` is a boolean vector that determines if a given element should be processed with
///         the atomic RMW op. Elements with `mask[i] == 0` are dropped (i.e., the atomic is not executed).
///         Similar to TT_AtomicRMWOp: Buffer atomic RMW ops load data at $ptr, do $rmw_op with $val, and store result to $ptr with
///         the specified memory semantics and scope. Atomic RMW ops return the pre-op value if used, otherwise the value is implicitly dropped.
///         Stride is the distance between the beginning of contiguous memory chunks. When performing a RMW, the `stride` is
///         the address difference between the first elements of each row in bytes. Compiler tries to obtain the `stride`
///         when it converts to the buffer ops because it is important for optimizing the cache memory access.
class BufferAtomicRMWOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Load from a scalar base pointer and a tensor offset
/// AMD Buffer load operation. Buffer store is similar to
///       a normal store but it accesses global memory via a scalar base pointer
///       and a tensor of offsets instead of a tensor of pointers. The other fields
///       are similar to a normal load, i.e., the `mask` is a boolean vector that
///       determines if a given element should be read from memory, and `other` is the
///       element that should be returned on lane `i` when `mask[i] == 0`.
///       Stride is the distance between the beginning of contiguous memory chunks.
///       When performing a load of a block, the `stride` is the address difference between
///       the first elements of each row in bytes. Compiler tries to obtain the `stride`
///       when it converts to the buffer ops because it is important for optimizing
///       the cache memory access.
class BufferLoadOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Load from a scalar base pointer and a tensor offset to shared memory
/// AMD Buffer load operation. Similar to amdgpu.buffer_load op but directly wirtes to shared memory instead of into registers.
class BufferLoadToLocalOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Store into scalar base pointer and a tensor offset
/// AMD Buffer store operation. Buffer store is similar to
///       normal store but it accesses global memory via a scalar base pointer
///       and a tensor of offsets instead of a tensor of pointers. The other fields
///       are similar to a normal store , i.e., the `mask` is a boolean vector that
///       determines if a given element should be written to memory, and `value` is the
///       tensor of elements that should be written on lane `i` when `mask[i] == 1`.
///       Stride is the distance between the beginning of contiguous memory chunks.
///       When performing a block store, the `stride` is the address difference between
///       the first elements of each row in bytes. Compiler tries to obtain the `stride`
///       when it converts to the buffer ops because it is important for optimizing
///       the cache memory access.
class BufferStoreOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// concat operation
/// The "concat" operation combines a list of source n-dimensional tensors into a single larger destination tensor.
/// 
///     All source tensors must have the same shape, element type, and encoding.
///     The concatenation dimension is inferred from the source and destination shapes provided by the user.
///     For example, two tensors of shape 64x128 can produce a destination shape of 128x128,
///     indicating concatenation along dimension 0; or 64x256, indicating concatenation along dimension 1.
/// 
///     Generally, source tensors passed as op arguments can be arranged into the resulting shape in multiple ways.
///     For example, given four tensors of shape 64x64:
///       concat s0<64x64>, s1<64x64>, s2<64x64>, s3<64x64> -> <128x128>
/// 
///     They can be laid out in different configurations within the result tensor:
///       1) s0 s1     2) s0 s2
///          s2 s3        s1 s3
/// 
///     From a logical tensor perspective, the source tensors are treated as elements of a tensor of tensors.
///     In other words, the 1-D array of input tensors is conceptually reshaped into an n-D grid.
///     The semantics of this op assume a row-major order (or its n-D generalization),
///     meaning the fastest-varying dimension is filled first, and the slowest-varying dimension is filled last.
///     In the example above, this corresponds to layout 1).
/// 
///     The source and destination tensors must have identical linear layouts at the CTA tile level.
///     That is, all base vectors for input dimensions must match, except for the register input dimension.
///     The register basis must align on the subset that defines the logical tensor shape of a single CTA tile.
/// 
///     This ensures that the concatenation is a no-op, meaning no data rearrangement among threads is required
///     to assemble the destination tensor with the given shape and layout.
///     However, the order of CTA tiles within the layout does not need to match between source and destination layouts.
///     It is the responsibility of the op's lowering logic to handle this correctly.
/// 
///     This op is designed to work on logical tensors directly, avoiding the need for complex layout reinterpretation or reshaping.
///     For example, the `tt.join` operation only supports concatenation along the innermost dimension,
///     and requires that the resulting innermost dimension provide 2 elements per thread, distributed across registers.
///     In contrast, this `concat` op imposes no constraints on the concatenation dimension or the size of dimensions.
/// 
///     * sources: a list of the input tensors.
/// 
///     Example 1:
/// 
///     ```mlir
///     #blocked = #ttg.blocked<{sizePerThread = [1, 8],
///         threadsPerWarp = [8, 8], warpsPerCTA = [4, 1], order = [1, 0]}>
///     %0 = amdgpu.concat %arg0, %arg1: tensor<32x64xf32, #blocked>,tensor<32x64xf32, #blocked>,
///       -> tensor<64x64xf32, #blocked>
///     ```
/// 
///     Example 2:
///     ```mlir
///     #src_layout = #ttg.linear<{register=[[0, 1], [0, 2], [0, 8], [0, 16], [0, 64], [64, 0]], lane=[[1, 0], [2, 0], [4, 0], [8, 0], [16, 0], [0, 4]], warp=[[0, 32], [32, 0]], block=[]}>
///     #dst_layout = #ttg.linear<{register=[[0, 1], [0, 2], [0, 8], [0, 16], [0, 64], [0, 128], [64, 0], [128, 0]], lane=[[1, 0], [2, 0], [4, 0], [8, 0], [16, 0], [0, 4]], warp=[[0, 32], [32, 0]], block=[]}>
///     %0 = amdgpu.concat %arg0, %arg1, %arg2, %arg3 : tensor<128x128xf16, #src_layout>, tensor<128x128xf16, #src_layout>, tensor<128x128xf16, #src_layout>,
///                                                     tensor<128x128xf16, #src_layout> -> tensor<256x256xf16, #dst_layout>
///     ```
class ConcatOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Conditionally set barriers to synchronize partial threads in a block
/// condBarrierOp sets barrier instruction only when the given argument is true.
///       This provides a way to synchronize partial threads in a block, deliberately
///       diverges the execution sequences. However, user should guarantee all threads
///       converge at the end by calling condBarrierOp(true) with the remaining threads.
///       Conceptually, this is similar to having an execution barrier inside an if statement.
///       This op allows us to avoid blocking the whole block when suitable to help scheduling.
///       NB. This doesn't set any memory fence.
class CondBarrierOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// extract slice operation
/// The "extract_slice" operation enables extracting a slice of a tensor in
///     registers.
/// 
///     The "extract_slice" operation supports the following arguments:
/// 
///     * source: the base tensor on which to create a view tensor
///     * offsets: offsets into the base tensor at which to create the view
/// 
///     In distributed layouts, tensors are divided into CTA tiles.
///     A CTA tile represents the smallest contiguous portion of a tensor that is
///     distributed across all threads and warps within a workgroup.
///     The ExtractSlice operation extracts a portion of the tensor that is a
///     multiple of CTA tiles.
/// 
///     The source and destination must have matching linear layouts at the CTA
///     tile level. This ensures that the extract_slice is a no-op, meaning no data
///     rearrangement between threads is required to extract the destination tensor
///     with the given shape and layout.
/// 
///       +-------+-------+
///       |  W0   |  W1   |
///       |       |       |
///       |   +   |   +   |
///       |  W2   |  W3   |  <-- Single CTA tile (distributed across warps W0-W3)
///       |       |       |
///       |   +   |   +   |
///       |       |       |
///       +-------+-------+
///       |          Source Tensor                    Extracted Slice
///       |             .                           +--------------+
///       |             .                           |  W0  |  W1   |
///       |             .                           |      |       |
///       |                                         |  +   |   +   |
///       |                                         |  W2  |  W3   |
///       |                                         |      |       |
///       |                                         |  +   |   +   |
///       |                                         |      |       |
///       |                                         +-------+------+
///       |                                         |  W0  |   W1  |
///       |                                         |      |       |
///       |                                         |  +   |   +   |
///       |                                         |  W2     W3   |
///       |                                         |      |       |
///       |                                         |  +   |   +   |
///       |                                         |      |       |
///       |                                         +--------------+
/// 
/// 
///     This op is designed to work on logical tensors directly, avoiding the need
///     for complex layout reinterpretation or reshaping. For example, the tt.split
///     operation only supports splitting along the innermost dimension,
///     and requires that the resulting innermost dimension provide 2 elements per thread,
///     distributed across registers. In contrast, extract_slice op imposes no constraints
///     on the extraction dimension or the size of dimensions.
/// 
///     Example 1:
/// 
///     ```mlir
///     #blocked = #ttg.blocked<{sizePerThread = [1, 8],
///         threadsPerWarp = [4, 16], warpsPerCTA = [4, 1], order = [0, 1]}>
///     #blocked1 = #ttg.blocked<{sizePerThread = [1, 8],
///         threadsPerWarp = [16, 4], warpsPerCTA = [4, 1], order = [0, 1]}>
///     %1 = ttg.convert_layout %0 : tensor<128x128xf16, #blocked>
///         -> tensor<128x128xf16, #blocked1>
///     // create a slice of base tensor %1 with static offsets
///     %2 = amdgpu.extract_slice %0 [0, 0] :
///       tensor<128x128xf16, #blocked1> to tensor<128x32xf16, #blocked1>
///     ```
/// 
///     Example 1 shows how "extract_slice" operation may be used. In this example a
///     new slice of 128x32 is created. "extract_slice" works on tensors
///     where the desired slice has the same layout on a CTA tile as the source tensor.
///     "%0" cannot be sliced directly as the resulting slice does not satisfy this condition.
///     Therefore it needs to be converted to a layout suitable for slicing.
///     "#blocked1" layout is appropriate for this as it keeps the
///     sizePerThread the same thus keeping coalescing properties the same.
///     In order to utilize all threads in a warp, "threadsPerWarp" is set to
///     [16,4] for this new layout. This layout conversion carried out before
///     using "extract_slice" ensures slicing still uses all threads efficiently. The
///     size of the slice is determined by the result type.
class ExtractSliceOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Perform transpose of register values belonging to each threads
/// This operation performs a layout transpose over values in registers per thread.
///     Specifically, given the input layout's blocked layout, it transposes the two last dimensions(rank-1 and rank-2)
///     along the register dimension of the underlying linear layout.
/// 
///     Conversion example:
///     * input layout: blocked layout with sizePerThread=[2, 2], order=[0, 1]. It's linear layout register bases = [[1, 0], [2, 0], [0, 1], [0, 2]]
///     * output layout: same thread and warp bases as in input, register bases = [[0, 1], [0, 2], [1, 0], [2, 0]]
/// 
///     This operation enables efficient coalesced loading from HBM with following vectorized writing to shared memory
///     in cases when HBM and shared memory order differ and target AMD hardware does not natively support this transposition.
///     This is a specific variant of ttg.convert_layout and will be converted to ttg.convert_layout when lowering to llvm.
///     We do not want this conversion to be optimized out, because we need to explicitly materialize instructions
///     to transpose within each thread after loading from HBM and before writing to shared memory.
class InThreadTransposeOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// A placeholder op for instruction scheduling hints within a basic block
/// A placeholder op for instruction scheduling hints applied to instructions within
///     a basic block where the placeholder op is located. This op is primarily intended
///     to be used to adjust instruction scheduling inside the resulting main loop
///     of a `tt.dot` operation. It's easier to identify dot ops at a high level and, thus,
///     to mark intended scheduling regions. The hint ops are eventually lowered
///     into LLVM AMDGPU instruction scheduling primitives, which are meant to control
///     how different kinds of instructions (valu/mfma, global/shared memory, etc.) should
///     interleave for better instruction level parallelism.
class InstructionSchedHint;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Load a transposed packed tensor from shared memory into a distributed tensor
/// Requires a M/N packed and M/N contiguous tensor in shared memory and will yield a K packed K contiguous tensor in registers.
///       The packing change will change the shape of the tensor by doubling the M/N dimension and halving the K dimension.
///       For example if A is 16x64 in shared memory, the result of this operation will be 32x32.
class LocalLoadPackedTransposedOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace amdgpu {
/// Convert an mxfp tensor to bf16/fp16
/// Compute the bf16 encoded in the given mxfp number as per
///     https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf
class UpcastMXFPOp;
} // namespace amdgpu
} // namespace triton
} // namespace mlir
#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::BufferAtomicCASOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BufferAtomicCASOpGenericAdaptorBase {
public:
  struct Properties {
    using scopeTy = ::mlir::triton::MemSyncScopeAttr;
    scopeTy scope;

    auto getScope() const {
      auto &propStorage = this->scope;
      return ::llvm::cast<::mlir::triton::MemSyncScopeAttr>(propStorage);
    }
    void setScope(const ::mlir::triton::MemSyncScopeAttr &propValue) {
      this->scope = propValue;
    }
    using semTy = ::mlir::triton::MemSemanticAttr;
    semTy sem;

    auto getSem() const {
      auto &propStorage = this->sem;
      return ::llvm::cast<::mlir::triton::MemSemanticAttr>(propStorage);
    }
    void setSem(const ::mlir::triton::MemSemanticAttr &propValue) {
      this->sem = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.scope == this->scope &&
        rhs.sem == this->sem &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  BufferAtomicCASOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.buffer_atomic_cas", odsAttrs.getContext());
  }

  BufferAtomicCASOpGenericAdaptorBase(BufferAtomicCASOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::MemSemanticAttr getSemAttr() {
    auto attr = ::llvm::cast<::mlir::triton::MemSemanticAttr>(getProperties().sem);
    return attr;
  }

  ::mlir::triton::MemSemantic getSem();
  ::mlir::triton::MemSyncScopeAttr getScopeAttr() {
    auto attr = ::llvm::cast<::mlir::triton::MemSyncScopeAttr>(getProperties().scope);
    return attr;
  }

  ::mlir::triton::MemSyncScope getScope();
};
} // namespace detail
template <typename RangeT>
class BufferAtomicCASOpGenericAdaptor : public detail::BufferAtomicCASOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BufferAtomicCASOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_cmp = 2;
  static constexpr int odsIndex_val = 3;
  static constexpr int odsIndex_stride = 4;
public:
  BufferAtomicCASOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BufferAtomicCASOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BufferAtomicCASOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BufferAtomicCASOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : BufferAtomicCASOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BufferAtomicCASOpGenericAdaptor(RangeT values, const BufferAtomicCASOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BufferAtomicCASOp, typename = std::enable_if_t<std::is_same_v<LateInst, BufferAtomicCASOp>>>
  BufferAtomicCASOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  ValueT getOffsets() {
    return (*getODSOperands(1).begin());
  }

  ValueT getCmp() {
    return (*getODSOperands(2).begin());
  }

  ValueT getVal() {
    return (*getODSOperands(3).begin());
  }

  ValueT getStride() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BufferAtomicCASOpAdaptor : public BufferAtomicCASOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BufferAtomicCASOpGenericAdaptor::BufferAtomicCASOpGenericAdaptor;
  BufferAtomicCASOpAdaptor(BufferAtomicCASOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BufferAtomicCASOp : public ::mlir::Op<BufferAtomicCASOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<4>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::OpTrait::SameLoadStoreOperandsAndResultEncoding, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BufferAtomicCASOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BufferAtomicCASOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_cmp = 2;
  static constexpr int odsIndex_val = 3;
  static constexpr int odsIndex_stride = 4;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("scope"), ::llvm::StringRef("sem")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getScopeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getScopeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getSemAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getSemAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.buffer_atomic_cas");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::TensorType> getOffsets() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getCmp() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getVal() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(3).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getStride() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getOffsetsMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getCmpMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getValMutable() {
    auto range = getODSOperandIndexAndLength(3);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getStrideMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::MemSemanticAttr getSemAttr() {
    return ::llvm::cast<::mlir::triton::MemSemanticAttr>(getProperties().sem);
  }

  ::mlir::triton::MemSemantic getSem();
  ::mlir::triton::MemSyncScopeAttr getScopeAttr() {
    return ::llvm::cast<::mlir::triton::MemSyncScopeAttr>(getProperties().scope);
  }

  ::mlir::triton::MemSyncScope getScope();
  void setSemAttr(::mlir::triton::MemSemanticAttr attr) {
    getProperties().sem = attr;
  }

  void setSem(::mlir::triton::MemSemantic attrValue);
  void setScopeAttr(::mlir::triton::MemSyncScopeAttr attr) {
    getProperties().scope = attr;
  }

  void setScope(::mlir::triton::MemSyncScope attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope);
  static BufferAtomicCASOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope);
  static BufferAtomicCASOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope);
  static BufferAtomicCASOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope);
  static BufferAtomicCASOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope);
  static BufferAtomicCASOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope);
  static BufferAtomicCASOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope);
  static BufferAtomicCASOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope);
  static BufferAtomicCASOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value cmp, ::mlir::Value val, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferAtomicCASOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferAtomicCASOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferAtomicCASOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferAtomicCASOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 2 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::BufferAtomicCASOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::BufferAtomicRMWOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BufferAtomicRMWOpGenericAdaptorBase {
public:
  struct Properties {
    using atomic_rmw_opTy = ::mlir::triton::RMWOpAttr;
    atomic_rmw_opTy atomic_rmw_op;

    auto getAtomicRmwOp() const {
      auto &propStorage = this->atomic_rmw_op;
      return ::llvm::cast<::mlir::triton::RMWOpAttr>(propStorage);
    }
    void setAtomicRmwOp(const ::mlir::triton::RMWOpAttr &propValue) {
      this->atomic_rmw_op = propValue;
    }
    using scopeTy = ::mlir::triton::MemSyncScopeAttr;
    scopeTy scope;

    auto getScope() const {
      auto &propStorage = this->scope;
      return ::llvm::cast<::mlir::triton::MemSyncScopeAttr>(propStorage);
    }
    void setScope(const ::mlir::triton::MemSyncScopeAttr &propValue) {
      this->scope = propValue;
    }
    using semTy = ::mlir::triton::MemSemanticAttr;
    semTy sem;

    auto getSem() const {
      auto &propStorage = this->sem;
      return ::llvm::cast<::mlir::triton::MemSemanticAttr>(propStorage);
    }
    void setSem(const ::mlir::triton::MemSemanticAttr &propValue) {
      this->sem = propValue;
    }
    using operandSegmentSizesTy = std::array<int32_t, 5>;
    operandSegmentSizesTy operandSegmentSizes;
    ::llvm::ArrayRef<int32_t> getOperandSegmentSizes() const {
      auto &propStorage = this->operandSegmentSizes;
      return propStorage;
    }
    void setOperandSegmentSizes(::llvm::ArrayRef<int32_t> propValue) {
      auto &propStorage = this->operandSegmentSizes;
      ::llvm::copy(propValue, propStorage.begin());
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.atomic_rmw_op == this->atomic_rmw_op &&
        rhs.scope == this->scope &&
        rhs.sem == this->sem &&
        rhs.operandSegmentSizes == this->operandSegmentSizes &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  BufferAtomicRMWOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.buffer_atomic_rmw", odsAttrs.getContext());
  }

  BufferAtomicRMWOpGenericAdaptorBase(BufferAtomicRMWOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::RMWOpAttr getAtomicRmwOpAttr() {
    auto attr = ::llvm::cast<::mlir::triton::RMWOpAttr>(getProperties().atomic_rmw_op);
    return attr;
  }

  ::mlir::triton::RMWOp getAtomicRmwOp();
  ::mlir::triton::MemSemanticAttr getSemAttr() {
    auto attr = ::llvm::cast<::mlir::triton::MemSemanticAttr>(getProperties().sem);
    return attr;
  }

  ::mlir::triton::MemSemantic getSem();
  ::mlir::triton::MemSyncScopeAttr getScopeAttr() {
    auto attr = ::llvm::cast<::mlir::triton::MemSyncScopeAttr>(getProperties().scope);
    return attr;
  }

  ::mlir::triton::MemSyncScope getScope();
};
} // namespace detail
template <typename RangeT>
class BufferAtomicRMWOpGenericAdaptor : public detail::BufferAtomicRMWOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BufferAtomicRMWOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_value = 2;
  static constexpr int odsIndex_stride = 3;
  static constexpr int odsIndex_mask = 4;
public:
  BufferAtomicRMWOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BufferAtomicRMWOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BufferAtomicRMWOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BufferAtomicRMWOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs) : BufferAtomicRMWOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BufferAtomicRMWOpGenericAdaptor(RangeT values, const BufferAtomicRMWOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BufferAtomicRMWOp, typename = std::enable_if_t<std::is_same_v<LateInst, BufferAtomicRMWOp>>>
  BufferAtomicRMWOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  ValueT getOffsets() {
    return (*getODSOperands(1).begin());
  }

  ValueT getValue() {
    return (*getODSOperands(2).begin());
  }

  ValueT getStride() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  ValueT getMask() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BufferAtomicRMWOpAdaptor : public BufferAtomicRMWOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BufferAtomicRMWOpGenericAdaptor::BufferAtomicRMWOpGenericAdaptor;
  BufferAtomicRMWOpAdaptor(BufferAtomicRMWOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BufferAtomicRMWOp : public ::mlir::Op<BufferAtomicRMWOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::AttrSizedOperandSegments, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::OpTrait::SameLoadStoreOperandsAndResultEncoding, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BufferAtomicRMWOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BufferAtomicRMWOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_value = 2;
  static constexpr int odsIndex_stride = 3;
  static constexpr int odsIndex_mask = 4;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("atomic_rmw_op"), ::llvm::StringRef("scope"), ::llvm::StringRef("sem"), ::llvm::StringRef("operandSegmentSizes")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getAtomicRmwOpAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getAtomicRmwOpAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getScopeAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getScopeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr getSemAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr getSemAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  ::mlir::StringAttr getOperandSegmentSizesAttrName() {
   return (*this)->getName().getAttributeNames().back();
  }

  static ::mlir::StringAttr getOperandSegmentSizesAttrName(::mlir::OperationName name) {
   return name.getAttributeNames().back();
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.buffer_atomic_rmw");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::TensorType> getOffsets() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getValue() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getStride() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getMask() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getOffsetsMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getValueMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getStrideMutable();
  ::mlir::MutableOperandRange getMaskMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::RMWOpAttr getAtomicRmwOpAttr() {
    return ::llvm::cast<::mlir::triton::RMWOpAttr>(getProperties().atomic_rmw_op);
  }

  ::mlir::triton::RMWOp getAtomicRmwOp();
  ::mlir::triton::MemSemanticAttr getSemAttr() {
    return ::llvm::cast<::mlir::triton::MemSemanticAttr>(getProperties().sem);
  }

  ::mlir::triton::MemSemantic getSem();
  ::mlir::triton::MemSyncScopeAttr getScopeAttr() {
    return ::llvm::cast<::mlir::triton::MemSyncScopeAttr>(getProperties().scope);
  }

  ::mlir::triton::MemSyncScope getScope();
  void setAtomicRmwOpAttr(::mlir::triton::RMWOpAttr attr) {
    getProperties().atomic_rmw_op = attr;
  }

  void setAtomicRmwOp(::mlir::triton::RMWOp attrValue);
  void setSemAttr(::mlir::triton::MemSemanticAttr attr) {
    getProperties().sem = attr;
  }

  void setSem(::mlir::triton::MemSemantic attrValue);
  void setScopeAttr(::mlir::triton::MemSyncScopeAttr attr) {
    getProperties().scope = attr;
  }

  void setScope(::mlir::triton::MemSyncScope attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::triton::RMWOpAttr atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::triton::RMWOpAttr atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::triton::RMWOpAttr atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::triton::RMWOpAttr atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::triton::RMWOpAttr atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::triton::RMWOpAttr atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemanticAttr sem, ::mlir::triton::MemSyncScopeAttr scope, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::triton::RMWOp atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::triton::RMWOp atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::triton::RMWOp atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::triton::RMWOp atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::triton::RMWOp atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope, /*optional*/::mlir::Value mask);
  static BufferAtomicRMWOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::triton::RMWOp atomic_rmw_op, ::mlir::Value ptr, ::mlir::Value offsets, ::mlir::Value value, /*optional*/::mlir::Value stride, ::mlir::triton::MemSemantic sem, ::mlir::triton::MemSyncScope scope, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferAtomicRMWOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferAtomicRMWOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferAtomicRMWOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferAtomicRMWOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 3 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::BufferAtomicRMWOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::BufferLoadOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BufferLoadOpGenericAdaptorBase {
public:
  struct Properties {
    using cacheTy = ::mlir::triton::CacheModifierAttr;
    cacheTy cache;

    auto getCache() const {
      auto &propStorage = this->cache;
      return ::llvm::dyn_cast_or_null<::mlir::triton::CacheModifierAttr>(propStorage);
    }
    void setCache(const ::mlir::triton::CacheModifierAttr &propValue) {
      this->cache = propValue;
    }
    using operandSegmentSizesTy = std::array<int32_t, 5>;
    operandSegmentSizesTy operandSegmentSizes;
    ::llvm::ArrayRef<int32_t> getOperandSegmentSizes() const {
      auto &propStorage = this->operandSegmentSizes;
      return propStorage;
    }
    void setOperandSegmentSizes(::llvm::ArrayRef<int32_t> propValue) {
      auto &propStorage = this->operandSegmentSizes;
      ::llvm::copy(propValue, propStorage.begin());
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache == this->cache &&
        rhs.operandSegmentSizes == this->operandSegmentSizes &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  BufferLoadOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.buffer_load", odsAttrs.getContext());
  }

  BufferLoadOpGenericAdaptorBase(BufferLoadOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::CacheModifierAttr getCacheAttr();
  ::mlir::triton::CacheModifier getCache();
};
} // namespace detail
template <typename RangeT>
class BufferLoadOpGenericAdaptor : public detail::BufferLoadOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BufferLoadOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_stride = 2;
  static constexpr int odsIndex_mask = 3;
  static constexpr int odsIndex_other = 4;
public:
  BufferLoadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BufferLoadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BufferLoadOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BufferLoadOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs) : BufferLoadOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BufferLoadOpGenericAdaptor(RangeT values, const BufferLoadOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BufferLoadOp, typename = std::enable_if_t<std::is_same_v<LateInst, BufferLoadOp>>>
  BufferLoadOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  ValueT getOffsets() {
    return (*getODSOperands(1).begin());
  }

  ValueT getStride() {
    auto operands = getODSOperands(2);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  ValueT getMask() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  ValueT getOther() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BufferLoadOpAdaptor : public BufferLoadOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BufferLoadOpGenericAdaptor::BufferLoadOpGenericAdaptor;
  BufferLoadOpAdaptor(BufferLoadOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BufferLoadOp : public ::mlir::Op<BufferLoadOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<2>::Impl, ::mlir::OpTrait::AttrSizedOperandSegments, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::OpTrait::SameLoadStoreOperandsAndResultEncoding, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BufferLoadOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BufferLoadOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_stride = 2;
  static constexpr int odsIndex_mask = 3;
  static constexpr int odsIndex_other = 4;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache"), ::llvm::StringRef("operandSegmentSizes")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getOperandSegmentSizesAttrName() {
   return (*this)->getName().getAttributeNames().back();
  }

  static ::mlir::StringAttr getOperandSegmentSizesAttrName(::mlir::OperationName name) {
   return name.getAttributeNames().back();
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.buffer_load");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::TensorType> getOffsets() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getStride() {
    auto operands = getODSOperands(2);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getMask() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getOther() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getOffsetsMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getStrideMutable();
  ::mlir::MutableOperandRange getMaskMutable();
  ::mlir::MutableOperandRange getOtherMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::CacheModifierAttr getCacheAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::triton::CacheModifierAttr>(getProperties().cache);
  }

  ::mlir::triton::CacheModifier getCache();
  void setCacheAttr(::mlir::triton::CacheModifierAttr attr) {
    getProperties().cache = attr;
  }

  void setCache(::mlir::triton::CacheModifier attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static BufferLoadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferLoadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferLoadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferLoadOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferLoadOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static void populateDefaultProperties(::mlir::OperationName opName, Properties &properties);
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::BufferLoadOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::BufferLoadToLocalOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BufferLoadToLocalOpGenericAdaptorBase {
public:
  struct Properties {
    using cacheTy = ::mlir::triton::CacheModifierAttr;
    cacheTy cache;

    auto getCache() const {
      auto &propStorage = this->cache;
      return ::llvm::dyn_cast_or_null<::mlir::triton::CacheModifierAttr>(propStorage);
    }
    void setCache(const ::mlir::triton::CacheModifierAttr &propValue) {
      this->cache = propValue;
    }
    using operandSegmentSizesTy = std::array<int32_t, 6>;
    operandSegmentSizesTy operandSegmentSizes;
    ::llvm::ArrayRef<int32_t> getOperandSegmentSizes() const {
      auto &propStorage = this->operandSegmentSizes;
      return propStorage;
    }
    void setOperandSegmentSizes(::llvm::ArrayRef<int32_t> propValue) {
      auto &propStorage = this->operandSegmentSizes;
      ::llvm::copy(propValue, propStorage.begin());
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache == this->cache &&
        rhs.operandSegmentSizes == this->operandSegmentSizes &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  BufferLoadToLocalOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.buffer_load_to_local", odsAttrs.getContext());
  }

  BufferLoadToLocalOpGenericAdaptorBase(BufferLoadToLocalOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::CacheModifierAttr getCacheAttr();
  ::mlir::triton::CacheModifier getCache();
};
} // namespace detail
template <typename RangeT>
class BufferLoadToLocalOpGenericAdaptor : public detail::BufferLoadToLocalOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BufferLoadToLocalOpGenericAdaptorBase;
  static constexpr int odsIndex_dest = 0;
  static constexpr int odsIndex_ptr = 1;
  static constexpr int odsIndex_offsets = 2;
  static constexpr int odsIndex_mask = 3;
  static constexpr int odsIndex_other = 4;
  static constexpr int odsIndex_stride = 5;
public:
  BufferLoadToLocalOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BufferLoadToLocalOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BufferLoadToLocalOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BufferLoadToLocalOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs) : BufferLoadToLocalOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BufferLoadToLocalOpGenericAdaptor(RangeT values, const BufferLoadToLocalOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BufferLoadToLocalOp, typename = std::enable_if_t<std::is_same_v<LateInst, BufferLoadToLocalOp>>>
  BufferLoadToLocalOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getDest() {
    return (*getODSOperands(0).begin());
  }

  ValueT getPtr() {
    return (*getODSOperands(1).begin());
  }

  ValueT getOffsets() {
    return (*getODSOperands(2).begin());
  }

  ValueT getMask() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  ValueT getOther() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  ValueT getStride() {
    auto operands = getODSOperands(5);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BufferLoadToLocalOpAdaptor : public BufferLoadToLocalOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BufferLoadToLocalOpGenericAdaptor::BufferLoadToLocalOpGenericAdaptor;
  BufferLoadToLocalOpAdaptor(BufferLoadToLocalOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BufferLoadToLocalOp : public ::mlir::Op<BufferLoadToLocalOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::triton::gpu::AsyncTokenType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::AttrSizedOperandSegments, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::InferTypeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BufferLoadToLocalOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BufferLoadToLocalOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_dest = 0;
  static constexpr int odsIndex_ptr = 1;
  static constexpr int odsIndex_offsets = 2;
  static constexpr int odsIndex_mask = 3;
  static constexpr int odsIndex_other = 4;
  static constexpr int odsIndex_stride = 5;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache"), ::llvm::StringRef("operandSegmentSizes")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getOperandSegmentSizesAttrName() {
   return (*this)->getName().getAttributeNames().back();
  }

  static ::mlir::StringAttr getOperandSegmentSizesAttrName(::mlir::OperationName name) {
   return name.getAttributeNames().back();
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.buffer_load_to_local");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getDest() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::TensorType> getOffsets() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getMask() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getOther() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getStride() {
    auto operands = getODSOperands(5);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::OpOperand &getDestMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getOffsetsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getMaskMutable();
  ::mlir::MutableOperandRange getOtherMutable();
  ::mlir::MutableOperandRange getStrideMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType> getToken() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::CacheModifierAttr getCacheAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::triton::CacheModifierAttr>(getProperties().cache);
  }

  ::mlir::triton::CacheModifier getCache();
  void setCacheAttr(::mlir::triton::CacheModifierAttr attr) {
    getProperties().cache = attr;
  }

  void setCache(::mlir::triton::CacheModifier attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type token, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type token, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type token, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type token, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type token, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type token, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value dest, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value mask, /*optional*/::mlir::Value other, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache = ::mlir::triton::CacheModifier::NONE);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferLoadToLocalOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferLoadToLocalOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static void populateDefaultProperties(::mlir::OperationName opName, Properties &properties);
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::llvm::LogicalResult inferReturnTypes(::mlir::MLIRContext *context, ::std::optional<::mlir::Location> location, ::mlir::ValueRange operands, ::mlir::DictionaryAttr attributes, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions, ::llvm::SmallVectorImpl<::mlir::Type>&inferredReturnTypes);
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::BufferLoadToLocalOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::BufferStoreOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BufferStoreOpGenericAdaptorBase {
public:
  struct Properties {
    using cacheTy = ::mlir::triton::CacheModifierAttr;
    cacheTy cache;

    auto getCache() const {
      auto &propStorage = this->cache;
      return ::llvm::dyn_cast_or_null<::mlir::triton::CacheModifierAttr>(propStorage);
    }
    void setCache(const ::mlir::triton::CacheModifierAttr &propValue) {
      this->cache = propValue;
    }
    using operandSegmentSizesTy = std::array<int32_t, 5>;
    operandSegmentSizesTy operandSegmentSizes;
    ::llvm::ArrayRef<int32_t> getOperandSegmentSizes() const {
      auto &propStorage = this->operandSegmentSizes;
      return propStorage;
    }
    void setOperandSegmentSizes(::llvm::ArrayRef<int32_t> propValue) {
      auto &propStorage = this->operandSegmentSizes;
      ::llvm::copy(propValue, propStorage.begin());
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache == this->cache &&
        rhs.operandSegmentSizes == this->operandSegmentSizes &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  BufferStoreOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.buffer_store", odsAttrs.getContext());
  }

  BufferStoreOpGenericAdaptorBase(BufferStoreOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::CacheModifierAttr getCacheAttr();
  ::mlir::triton::CacheModifier getCache();
};
} // namespace detail
template <typename RangeT>
class BufferStoreOpGenericAdaptor : public detail::BufferStoreOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BufferStoreOpGenericAdaptorBase;
  static constexpr int odsIndex_value = 0;
  static constexpr int odsIndex_ptr = 1;
  static constexpr int odsIndex_offsets = 2;
  static constexpr int odsIndex_stride = 3;
  static constexpr int odsIndex_mask = 4;
public:
  BufferStoreOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BufferStoreOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BufferStoreOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BufferStoreOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs) : BufferStoreOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BufferStoreOpGenericAdaptor(RangeT values, const BufferStoreOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BufferStoreOp, typename = std::enable_if_t<std::is_same_v<LateInst, BufferStoreOp>>>
  BufferStoreOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getValue() {
    return (*getODSOperands(0).begin());
  }

  ValueT getPtr() {
    return (*getODSOperands(1).begin());
  }

  ValueT getOffsets() {
    return (*getODSOperands(2).begin());
  }

  ValueT getStride() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  ValueT getMask() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BufferStoreOpAdaptor : public BufferStoreOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BufferStoreOpGenericAdaptor::BufferStoreOpGenericAdaptor;
  BufferStoreOpAdaptor(BufferStoreOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BufferStoreOp : public ::mlir::Op<BufferStoreOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<3>::Impl, ::mlir::OpTrait::AttrSizedOperandSegments, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::OpTrait::SameLoadStoreOperandsEncoding, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BufferStoreOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BufferStoreOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_value = 0;
  static constexpr int odsIndex_ptr = 1;
  static constexpr int odsIndex_offsets = 2;
  static constexpr int odsIndex_stride = 3;
  static constexpr int odsIndex_mask = 4;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache"), ::llvm::StringRef("operandSegmentSizes")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getOperandSegmentSizesAttrName() {
   return (*this)->getName().getAttributeNames().back();
  }

  static ::mlir::StringAttr getOperandSegmentSizesAttrName(::mlir::OperationName name) {
   return name.getAttributeNames().back();
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.buffer_store");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getValue() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::TensorType> getOffsets() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::TensorType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getStride() {
    auto operands = getODSOperands(3);
    return operands.empty() ? ::mlir::TypedValue<::mlir::IntegerType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*operands.begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getMask() {
    auto operands = getODSOperands(4);
    return operands.empty() ? ::mlir::TypedValue<::mlir::RankedTensorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*operands.begin());
  }

  ::mlir::OpOperand &getValueMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getOffsetsMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getStrideMutable();
  ::mlir::MutableOperandRange getMaskMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::CacheModifierAttr getCacheAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::triton::CacheModifierAttr>(getProperties().cache);
  }

  ::mlir::triton::CacheModifier getCache();
  void setCacheAttr(::mlir::triton::CacheModifierAttr attr) {
    getProperties().cache = attr;
  }

  void setCache(::mlir::triton::CacheModifier attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifierAttr cache, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask);
  static BufferStoreOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value value, ::mlir::Value ptr, ::mlir::Value offsets, /*optional*/::mlir::Value stride, ::mlir::triton::CacheModifier cache, /*optional*/::mlir::Value mask);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferStoreOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BufferStoreOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferStoreOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BufferStoreOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static void populateDefaultProperties(::mlir::OperationName opName, Properties &properties);
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::BufferStoreOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::ConcatOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ConcatOpGenericAdaptorBase {
public:
  using Properties = ::mlir::EmptyProperties;
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ConcatOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.concat", odsAttrs.getContext());
  }

  ConcatOpGenericAdaptorBase(ConcatOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

};
} // namespace detail
template <typename RangeT>
class ConcatOpGenericAdaptor : public detail::ConcatOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ConcatOpGenericAdaptorBase;
  static constexpr int odsIndex_sources = 0;
public:
  ConcatOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ConcatOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ConcatOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ConcatOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ConcatOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ConcatOpGenericAdaptor(RangeT values, const ConcatOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ConcatOp, typename = std::enable_if_t<std::is_same_v<LateInst, ConcatOp>>>
  ConcatOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  RangeT getSources() {
    return getODSOperands(0);
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ConcatOpAdaptor : public ConcatOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ConcatOpGenericAdaptor::ConcatOpGenericAdaptor;
  ConcatOpAdaptor(ConcatOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ConcatOp : public ::mlir::Op<ConcatOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::VariadicOperands, ::mlir::OpTrait::OpInvariants, ::mlir::ConditionallySpeculatable::Trait, ::mlir::OpTrait::AlwaysSpeculatableImplTrait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ConcatOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ConcatOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_sources = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    return {};
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.concat");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::Operation::operand_range getSources() {
    return getODSOperands(0);
  }

  ::mlir::MutableOperandRange getSourcesMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::ValueRange sources);
  static ConcatOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::ValueRange sources);
  static ConcatOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::ValueRange sources);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ConcatOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ConcatOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ConcatOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ConcatOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static void getCanonicalizationPatterns(::mlir::RewritePatternSet &results, ::mlir::MLIRContext *context);
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::ConcatOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::CondBarrierOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class CondBarrierOpGenericAdaptorBase {
public:
  using Properties = ::mlir::EmptyProperties;
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  CondBarrierOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.cond_barrier", odsAttrs.getContext());
  }

  CondBarrierOpGenericAdaptorBase(CondBarrierOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

};
} // namespace detail
template <typename RangeT>
class CondBarrierOpGenericAdaptor : public detail::CondBarrierOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::CondBarrierOpGenericAdaptorBase;
  static constexpr int odsIndex_pred = 0;
public:
  CondBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  CondBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : CondBarrierOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  CondBarrierOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : CondBarrierOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  CondBarrierOpGenericAdaptor(RangeT values, const CondBarrierOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = CondBarrierOp, typename = std::enable_if_t<std::is_same_v<LateInst, CondBarrierOp>>>
  CondBarrierOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPred() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class CondBarrierOpAdaptor : public CondBarrierOpGenericAdaptor<::mlir::ValueRange> {
public:
  using CondBarrierOpGenericAdaptor::CondBarrierOpGenericAdaptor;
  CondBarrierOpAdaptor(CondBarrierOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class CondBarrierOp : public ::mlir::Op<CondBarrierOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::OneOperand, ::mlir::OpTrait::OpInvariants> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = CondBarrierOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = CondBarrierOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_pred = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    return {};
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.cond_barrier");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::IntegerType> getPred() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(0).begin());
  }

  ::mlir::OpOperand &getPredMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value pred);
  static CondBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value pred);
  static CondBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value pred);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value pred);
  static CondBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value pred);
  static CondBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value pred);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static CondBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static CondBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static CondBarrierOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static CondBarrierOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::CondBarrierOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::ExtractSliceOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExtractSliceOpGenericAdaptorBase {
public:
  struct Properties {
    using static_offsetsTy = ::mlir::DenseI64ArrayAttr;
    static_offsetsTy static_offsets;

    auto getStaticOffsets() const {
      auto &propStorage = this->static_offsets;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticOffsets(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_offsets = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.static_offsets == this->static_offsets &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExtractSliceOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.extract_slice", odsAttrs.getContext());
  }

  ExtractSliceOpGenericAdaptorBase(ExtractSliceOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::DenseI64ArrayAttr getStaticOffsetsAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_offsets);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticOffsets();
};
} // namespace detail
template <typename RangeT>
class ExtractSliceOpGenericAdaptor : public detail::ExtractSliceOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExtractSliceOpGenericAdaptorBase;
  static constexpr int odsIndex_source = 0;
public:
  ExtractSliceOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExtractSliceOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExtractSliceOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExtractSliceOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : ExtractSliceOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExtractSliceOpGenericAdaptor(RangeT values, const ExtractSliceOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExtractSliceOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExtractSliceOp>>>
  ExtractSliceOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSource() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExtractSliceOpAdaptor : public ExtractSliceOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExtractSliceOpGenericAdaptor::ExtractSliceOpGenericAdaptor;
  ExtractSliceOpAdaptor(ExtractSliceOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExtractSliceOp : public ::mlir::Op<ExtractSliceOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::OneOperand, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::ConditionallySpeculatable::Trait, ::mlir::OpTrait::AlwaysSpeculatableImplTrait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExtractSliceOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExtractSliceOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_source = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("static_offsets")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getStaticOffsetsAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getStaticOffsetsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.extract_slice");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getSource() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::OpOperand &getSourceMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::DenseI64ArrayAttr getStaticOffsetsAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_offsets);
  }

  ::llvm::ArrayRef<int64_t> getStaticOffsets();
  void setStaticOffsetsAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_offsets = attr;
  }

  void setStaticOffsets(::llvm::ArrayRef<int64_t> attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value source, ::mlir::DenseI64ArrayAttr static_offsets);
  static ExtractSliceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value source, ::mlir::DenseI64ArrayAttr static_offsets);
  static ExtractSliceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value source, ::mlir::DenseI64ArrayAttr static_offsets);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value source, ::mlir::DenseI64ArrayAttr static_offsets);
  static ExtractSliceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value source, ::mlir::DenseI64ArrayAttr static_offsets);
  static ExtractSliceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value source, ::mlir::DenseI64ArrayAttr static_offsets);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value source, ::llvm::ArrayRef<int64_t> static_offsets);
  static ExtractSliceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value source, ::llvm::ArrayRef<int64_t> static_offsets);
  static ExtractSliceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value source, ::llvm::ArrayRef<int64_t> static_offsets);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value source, ::llvm::ArrayRef<int64_t> static_offsets);
  static ExtractSliceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value source, ::llvm::ArrayRef<int64_t> static_offsets);
  static ExtractSliceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value source, ::llvm::ArrayRef<int64_t> static_offsets);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExtractSliceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExtractSliceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExtractSliceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExtractSliceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static void getCanonicalizationPatterns(::mlir::RewritePatternSet &results, ::mlir::MLIRContext *context);
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  std::array<unsigned, 3> getArrayAttrMaxRanks() {
    unsigned rank = getSource().getType().getRank();
    return {rank, rank, rank};
  }
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::ExtractSliceOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::InThreadTransposeOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class InThreadTransposeOpGenericAdaptorBase {
public:
  using Properties = ::mlir::EmptyProperties;
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  InThreadTransposeOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.in_thread_transpose", odsAttrs.getContext());
  }

  InThreadTransposeOpGenericAdaptorBase(InThreadTransposeOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

};
} // namespace detail
template <typename RangeT>
class InThreadTransposeOpGenericAdaptor : public detail::InThreadTransposeOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::InThreadTransposeOpGenericAdaptorBase;
  static constexpr int odsIndex_src = 0;
public:
  InThreadTransposeOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  InThreadTransposeOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : InThreadTransposeOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  InThreadTransposeOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : InThreadTransposeOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  InThreadTransposeOpGenericAdaptor(RangeT values, const InThreadTransposeOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = InThreadTransposeOp, typename = std::enable_if_t<std::is_same_v<LateInst, InThreadTransposeOp>>>
  InThreadTransposeOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSrc() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class InThreadTransposeOpAdaptor : public InThreadTransposeOpGenericAdaptor<::mlir::ValueRange> {
public:
  using InThreadTransposeOpGenericAdaptor::InThreadTransposeOpGenericAdaptor;
  InThreadTransposeOpAdaptor(InThreadTransposeOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class InThreadTransposeOp : public ::mlir::Op<InThreadTransposeOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::OneOperand, ::mlir::OpTrait::OpInvariants, ::mlir::ConditionallySpeculatable::Trait, ::mlir::OpTrait::AlwaysSpeculatableImplTrait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = InThreadTransposeOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = InThreadTransposeOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_src = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    return {};
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.in_thread_transpose");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getSrc() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::OpOperand &getSrcMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src);
  static InThreadTransposeOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src);
  static InThreadTransposeOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src);
  static InThreadTransposeOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src);
  static InThreadTransposeOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static InThreadTransposeOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static InThreadTransposeOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static InThreadTransposeOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static InThreadTransposeOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
public:
  static mlir::triton::LinearLayout deduceOutputLayout(mlir::ArrayRef<int64_t> shape,
                               mlir::triton::gpu::BlockedEncodingAttr srcEncoding);
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::InThreadTransposeOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::InstructionSchedHint declarations
//===----------------------------------------------------------------------===//

namespace detail {
class InstructionSchedHintGenericAdaptorBase {
public:
  struct Properties {
    using variantTy = ::mlir::triton::amdgpu::SchedHintAttr;
    variantTy variant;

    auto getVariant() const {
      auto &propStorage = this->variant;
      return ::llvm::cast<::mlir::triton::amdgpu::SchedHintAttr>(propStorage);
    }
    void setVariant(const ::mlir::triton::amdgpu::SchedHintAttr &propValue) {
      this->variant = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.variant == this->variant &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  InstructionSchedHintGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.instruction_sched_hint", odsAttrs.getContext());
  }

  InstructionSchedHintGenericAdaptorBase(InstructionSchedHint op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::amdgpu::SchedHintAttr getVariantAttr() {
    auto attr = ::llvm::cast<::mlir::triton::amdgpu::SchedHintAttr>(getProperties().variant);
    return attr;
  }

  ::mlir::triton::amdgpu::SchedHint getVariant();
};
} // namespace detail
template <typename RangeT>
class InstructionSchedHintGenericAdaptor : public detail::InstructionSchedHintGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::InstructionSchedHintGenericAdaptorBase;
public:
  InstructionSchedHintGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  InstructionSchedHintGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : InstructionSchedHintGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  InstructionSchedHintGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : InstructionSchedHintGenericAdaptor(values, attrs, Properties{}, {}) {}

  InstructionSchedHintGenericAdaptor(RangeT values, const InstructionSchedHintGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = InstructionSchedHint, typename = std::enable_if_t<std::is_same_v<LateInst, InstructionSchedHint>>>
  InstructionSchedHintGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class InstructionSchedHintAdaptor : public InstructionSchedHintGenericAdaptor<::mlir::ValueRange> {
public:
  using InstructionSchedHintGenericAdaptor::InstructionSchedHintGenericAdaptor;
  InstructionSchedHintAdaptor(InstructionSchedHint op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class InstructionSchedHint : public ::mlir::Op<InstructionSchedHint, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::ZeroOperands, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = InstructionSchedHintAdaptor;
  template <typename RangeT>
  using GenericAdaptor = InstructionSchedHintGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("variant")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getVariantAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getVariantAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.instruction_sched_hint");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::amdgpu::SchedHintAttr getVariantAttr() {
    return ::llvm::cast<::mlir::triton::amdgpu::SchedHintAttr>(getProperties().variant);
  }

  ::mlir::triton::amdgpu::SchedHint getVariant();
  void setVariantAttr(::mlir::triton::amdgpu::SchedHintAttr attr) {
    getProperties().variant = attr;
  }

  void setVariant(::mlir::triton::amdgpu::SchedHint attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::triton::amdgpu::SchedHintAttr variant);
  static InstructionSchedHint create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::triton::amdgpu::SchedHintAttr variant);
  static InstructionSchedHint create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::triton::amdgpu::SchedHintAttr variant);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::triton::amdgpu::SchedHintAttr variant);
  static InstructionSchedHint create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::triton::amdgpu::SchedHintAttr variant);
  static InstructionSchedHint create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::triton::amdgpu::SchedHintAttr variant);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::triton::amdgpu::SchedHint variant);
  static InstructionSchedHint create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::triton::amdgpu::SchedHint variant);
  static InstructionSchedHint create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::triton::amdgpu::SchedHint variant);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::triton::amdgpu::SchedHint variant);
  static InstructionSchedHint create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::triton::amdgpu::SchedHint variant);
  static InstructionSchedHint create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::triton::amdgpu::SchedHint variant);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static InstructionSchedHint create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static InstructionSchedHint create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static InstructionSchedHint create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static InstructionSchedHint create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::InstructionSchedHint)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::LocalLoadPackedTransposedOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class LocalLoadPackedTransposedOpGenericAdaptorBase {
public:
  using Properties = ::mlir::EmptyProperties;
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  LocalLoadPackedTransposedOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.local_load_packed_tranposed", odsAttrs.getContext());
  }

  LocalLoadPackedTransposedOpGenericAdaptorBase(LocalLoadPackedTransposedOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

};
} // namespace detail
template <typename RangeT>
class LocalLoadPackedTransposedOpGenericAdaptor : public detail::LocalLoadPackedTransposedOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::LocalLoadPackedTransposedOpGenericAdaptorBase;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_token = 1;
public:
  LocalLoadPackedTransposedOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  LocalLoadPackedTransposedOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : LocalLoadPackedTransposedOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  LocalLoadPackedTransposedOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : LocalLoadPackedTransposedOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  LocalLoadPackedTransposedOpGenericAdaptor(RangeT values, const LocalLoadPackedTransposedOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = LocalLoadPackedTransposedOp, typename = std::enable_if_t<std::is_same_v<LateInst, LocalLoadPackedTransposedOp>>>
  LocalLoadPackedTransposedOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSrc() {
    return (*getODSOperands(0).begin());
  }

  ValueT getToken() {
    auto operands = getODSOperands(1);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class LocalLoadPackedTransposedOpAdaptor : public LocalLoadPackedTransposedOpGenericAdaptor<::mlir::ValueRange> {
public:
  using LocalLoadPackedTransposedOpGenericAdaptor::LocalLoadPackedTransposedOpGenericAdaptor;
  LocalLoadPackedTransposedOpAdaptor(LocalLoadPackedTransposedOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class LocalLoadPackedTransposedOp : public ::mlir::Op<LocalLoadPackedTransposedOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<1>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::OpTrait::LocalLoadTrait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = LocalLoadPackedTransposedOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = LocalLoadPackedTransposedOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_token = 1;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    return {};
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.local_load_packed_tranposed");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::gpu::MemDescType> getSrc() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::MemDescType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType> getToken() {
    auto operands = getODSOperands(1);
    return operands.empty() ? ::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::triton::gpu::AsyncTokenType>>(*operands.begin());
  }

  ::mlir::OpOperand &getSrcMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getTokenMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, Type retType, Value src);
  static LocalLoadPackedTransposedOp create(::mlir::OpBuilder &builder, ::mlir::Location location, Type retType, Value src);
  static LocalLoadPackedTransposedOp create(::mlir::ImplicitLocOpBuilder &builder, Type retType, Value src);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, /*optional*/::mlir::Value token);
  static LocalLoadPackedTransposedOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, /*optional*/::mlir::Value token);
  static LocalLoadPackedTransposedOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, /*optional*/::mlir::Value token);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, /*optional*/::mlir::Value token);
  static LocalLoadPackedTransposedOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, /*optional*/::mlir::Value token);
  static LocalLoadPackedTransposedOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, /*optional*/::mlir::Value token);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static LocalLoadPackedTransposedOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static LocalLoadPackedTransposedOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static LocalLoadPackedTransposedOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static LocalLoadPackedTransposedOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
public:
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::LocalLoadPackedTransposedOp)

namespace mlir {
namespace triton {
namespace amdgpu {

//===----------------------------------------------------------------------===//
// ::mlir::triton::amdgpu::UpcastMXFPOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class UpcastMXFPOpGenericAdaptorBase {
public:
  struct Properties {
    using fastMathTy = ::mlir::BoolAttr;
    fastMathTy fastMath;

    auto getFastMath() const {
      auto &propStorage = this->fastMath;
      return ::llvm::cast<::mlir::BoolAttr>(propStorage);
    }
    void setFastMath(const ::mlir::BoolAttr &propValue) {
      this->fastMath = propValue;
    }
    using fp_typeTy = ::mlir::triton::ScaleDotElemTypeAttr;
    fp_typeTy fp_type;

    auto getFpType() const {
      auto &propStorage = this->fp_type;
      return ::llvm::cast<::mlir::triton::ScaleDotElemTypeAttr>(propStorage);
    }
    void setFpType(const ::mlir::triton::ScaleDotElemTypeAttr &propValue) {
      this->fp_type = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.fastMath == this->fastMath &&
        rhs.fp_type == this->fp_type &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  UpcastMXFPOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("amdgpu.upcast_mxfp", odsAttrs.getContext());
  }

  UpcastMXFPOpGenericAdaptorBase(UpcastMXFPOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::triton::ScaleDotElemTypeAttr getFpTypeAttr() {
    auto attr = ::llvm::cast<::mlir::triton::ScaleDotElemTypeAttr>(getProperties().fp_type);
    return attr;
  }

  ::mlir::triton::ScaleDotElemType getFpType();
  ::mlir::BoolAttr getFastMathAttr() {
    auto attr = ::llvm::cast<::mlir::BoolAttr>(getProperties().fastMath);
    return attr;
  }

  bool getFastMath();
};
} // namespace detail
template <typename RangeT>
class UpcastMXFPOpGenericAdaptor : public detail::UpcastMXFPOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::UpcastMXFPOpGenericAdaptorBase;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_scale = 1;
public:
  UpcastMXFPOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  UpcastMXFPOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : UpcastMXFPOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  UpcastMXFPOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : UpcastMXFPOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  UpcastMXFPOpGenericAdaptor(RangeT values, const UpcastMXFPOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = UpcastMXFPOp, typename = std::enable_if_t<std::is_same_v<LateInst, UpcastMXFPOp>>>
  UpcastMXFPOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSrc() {
    return (*getODSOperands(0).begin());
  }

  ValueT getScale() {
    return (*getODSOperands(1).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class UpcastMXFPOpAdaptor : public UpcastMXFPOpGenericAdaptor<::mlir::ValueRange> {
public:
  using UpcastMXFPOpGenericAdaptor::UpcastMXFPOpGenericAdaptor;
  UpcastMXFPOpAdaptor(UpcastMXFPOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class UpcastMXFPOp : public ::mlir::Op<UpcastMXFPOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<2>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::ConditionallySpeculatable::Trait, ::mlir::OpTrait::AlwaysSpeculatableImplTrait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = UpcastMXFPOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = UpcastMXFPOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_scale = 1;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("fastMath"), ::llvm::StringRef("fp_type")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getFastMathAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getFastMathAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getFpTypeAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getFpTypeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("amdgpu.upcast_mxfp");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getSrc() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getScale() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(1).begin());
  }

  ::mlir::OpOperand &getSrcMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getScaleMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::triton::ScaleDotElemTypeAttr getFpTypeAttr() {
    return ::llvm::cast<::mlir::triton::ScaleDotElemTypeAttr>(getProperties().fp_type);
  }

  ::mlir::triton::ScaleDotElemType getFpType();
  ::mlir::BoolAttr getFastMathAttr() {
    return ::llvm::cast<::mlir::BoolAttr>(getProperties().fastMath);
  }

  bool getFastMath();
  void setFpTypeAttr(::mlir::triton::ScaleDotElemTypeAttr attr) {
    getProperties().fp_type = attr;
  }

  void setFpType(::mlir::triton::ScaleDotElemType attrValue);
  void setFastMathAttr(::mlir::BoolAttr attr) {
    getProperties().fastMath = attr;
  }

  void setFastMath(bool attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemTypeAttr fp_type, ::mlir::BoolAttr fastMath);
  static UpcastMXFPOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemTypeAttr fp_type, ::mlir::BoolAttr fastMath);
  static UpcastMXFPOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemTypeAttr fp_type, ::mlir::BoolAttr fastMath);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemTypeAttr fp_type, ::mlir::BoolAttr fastMath);
  static UpcastMXFPOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemTypeAttr fp_type, ::mlir::BoolAttr fastMath);
  static UpcastMXFPOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemTypeAttr fp_type, ::mlir::BoolAttr fastMath);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemType fp_type, bool fastMath);
  static UpcastMXFPOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemType fp_type, bool fastMath);
  static UpcastMXFPOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemType fp_type, bool fastMath);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemType fp_type, bool fastMath);
  static UpcastMXFPOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemType fp_type, bool fastMath);
  static UpcastMXFPOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value scale, ::mlir::triton::ScaleDotElemType fp_type, bool fastMath);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static UpcastMXFPOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static UpcastMXFPOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static UpcastMXFPOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static UpcastMXFPOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 2 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  static RankedTensorType deduceOutputType(
      TypedValue<RankedTensorType> inputTensor, ScaleDotElemType inputElemType, Type outputElemType);
};
} // namespace amdgpu
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::amdgpu::UpcastMXFPOp)


#endif // GET_OP_CLASSES

