#ifndef _SEG_HPP
#define _SEG_HPP

class Seg;

template<typename T>
class Array {
   size_t n;
   bool init_;
   T data[0];
public:
   Array() {}
   ~Array() {
      for(size_t i=0;i<n;i++) {
        data[i].T::~T();
      }
   }
   T& operator[](size_t n) {
      return data[n];
   }
   size_t size() { return n; }
   T *begin() { return data; }
   T *end() { return data+n; }
   bool init() { return init_; };
   friend class Seg;
};

class Seg {
	const char *seg;
	Seg() {}
	Seg(const Seg& s) {}
	Seg(Seg& s) {}
	void *managed_data = nullptr;
	void *allocate_(const char *name,size_t size,bool& init);
	void remove_(void *data);
public:
	Seg(const char *name, size_t size);
	Seg(const char *name) : Seg(name, 65536) {}
	~Seg() {}
	template<typename T>
	T *allocate(const char *name) {
		bool init;
		void *data = allocate_(name, sizeof(T), init);
		if(init)
			return new (data) T();
		else
			return (T *)data;
	}
	template<typename T>
	Array<T> *allocate_array(const char *name, size_t size) {
		bool init;
		void *data = allocate_(name, sizeof(Array<T>)+size*sizeof(T), init);
        Array<T> *array = (Array<T>*)data;
        array->init_ = init;
		if(init) {
            array->n = size;
            new (array->data) T[size];
			return new (data) Array<T>();
		} else {
			return array;
        }
	}
	void remove();
	template<typename T>
	void remove(T *data) {
        data->T::~T();
        remove_(data);
	}
};
#endif
