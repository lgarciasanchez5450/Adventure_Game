#define PY_SSIZE_T_CLEAN 
#include <C:\Users\Leo\AppData\Local\Programs\Python\Python310\include\Python.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define TABLE_SIZE 40000

// this is each entry in the hash table

typedef struct single_linked_list {
  PyObject* object;
  struct single_linked_list* next;
}linked_list_node;

/*
linked_list_node* ll_create(PyObject* object) {
  linked_list_node* ll_start = (linked_list_node*) malloc(sizeof(linked_list_node));
  ll_start->object = object;
  ll_start->next = NULL;
  return ll_start;
}
void ll_add(linked_list_node* llist,PyObject* object) {
  linked_list_node* curr = llist;
  while (curr->next!= NULL) { // while our current node has a next node to go to
    curr = curr->next; // we go to the next node
  }
  // once we get here we know that curr->next must be NULL because the while loop exited
  curr->next = ll_create(object);
}
 
void ll_destroy(linked_list_node* llist) {
    linked_list_node* curr = llist;
    while (curr!= NULL) { // while our current node has a next node to go to
        linked_list_node* next = curr->next;
        Py_DECREF(curr->object);
        free(curr);
        curr = next; // we go to the next node
    }
    // once we get here we know that curr->next must be NULL because the while loop exited

}*/
typedef struct entry_t {
  int key[2]; // this is the key of the entry
  int value; // this is the value of the entry ####this will be a pointer to the first item in a linked list 
  struct entry_t *next; // this for the purposes of a collision, where it
                        // represents a single-linked list to all the other
                        // entries that have the same hash value
} entry_t;

typedef struct {
  entry_t **entries; // this is actually a list to all the entries, the reason
                     // it is seen as a double-pointer is because we dont
                     // actually make the list until we create a hashtable
  // therefore this is a pointer, to the memory address of the start of the list
  // which means its a pointer to a pointer

} ht_t;
static ht_t* entity_chunks;
static bool initiated = false;
const int CHUNK_SIZE = 8;



static inline void delete_entry(entry_t* entry) {
    //ll_destroy(entry->value);
    free(entry);
}

// Function to create hash table, should return a pointer to the hashtable

// create a hash function for our key
// this can and SHOULD change for specific use cases but a default one should be
// set just in case

static unsigned int pcg32_random_r(signed int state) {
  // Calculate output function (XSH RR), uses old state for max ILP
  unsigned int result = ((state >> ((state >> 28) + 4)) ^ state) * 277803737;
  result = (result >> 22) ^ result;
  return result;
}

static unsigned int hash(int x, int y) {
  unsigned long int value = 0;
  value = (pcg32_random_r(x * 2147483629) + pcg32_random_r(y * 4282663)) % TABLE_SIZE;
  return value;
}

static ht_t* create_ht(void) {
  ht_t* hashtable = (ht_t*) malloc(sizeof(ht_t));
  hashtable->entries = (entry_t**) malloc(sizeof(entry_t *) * TABLE_SIZE);
  for (int i = 0; i < TABLE_SIZE; i++) {
    hashtable->entries[i] = NULL;
  }
  return hashtable;
}
static entry_t* ht_pair(int x,int y, int value) {
  entry_t* entry = (entry_t*) malloc(sizeof(entry_t) );
  entry->key[0] = x;
  entry->key[1] = y;
  entry->value = value;
  entry->next = NULL;
  return entry;
}
static void ht_set(ht_t* hashtable, int x, int y, int value) {
  unsigned int bucket = hash(x, y);

  // get the first value in the bucket which the hash value says
  entry_t* node = hashtable->entries[bucket];

  if (node == NULL) {
    hashtable->entries[bucket] = ht_pair(x, y, value);
    return;
  }

  entry_t* prev;
  while (node->next != NULL) {
    if ((node->key[0] == x ) && (node->key[1] == y)) {
      node->value = value; // when this is turned into a linked list again, the previous linked list must be destroyed first via ll_destroy
      return;
    }
    prev = node;
    node = node -> next;
  }
 
  prev->next = ht_pair(x, y, value);
}

//returns NULL when error occured and (int *) 1 when successful
static int* ht_del(ht_t* hashtable,int x,int y){
    unsigned int bucket = hash(x, y);

    // get the first value in the bucket which the
    // hash value says
    entry_t* node = hashtable->entries[bucket];


    if (node == NULL) {
      return NULL;
    }

    entry_t* prev;
    while (node->next != NULL) {
      if ((node->key[0] == x) && (node->key[1] == y)) {
        prev->next = node->next;
        delete_entry(node);
        return (int *) 1;
      }
      prev = node;
      node = node->next;
        // walk to next point
    }
    return NULL;
}
// will return (int*) -1 if error else , return int
static int* ht_get(ht_t *hashtable, int x, int y) {
  unsigned int bucket = hash(x, y);

  // get the first value in the bucket which the
  // hash value says
  entry_t* node = hashtable->entries[bucket];

  if (node == NULL) {
    return NULL;
  }
  while (node != NULL) {
    if ((node->key[0] == x) && (node->key[1] == y)) {
      
      return &(node->value);
    }
    node = node->next;
    // walk to next point
  }
  return NULL;
}

static void ht_get_collisions(ht_t *hashtable,int count_over) {
  int proper_collisions = 0;
  unsigned int min = 0xffffffff;
  unsigned int max = 0;
  
  double avg, stddev;
  avg = 0;
  stddev = 0;
  for (int bucket = 0; bucket < TABLE_SIZE; bucket++) {
    entry_t *node = hashtable->entries[bucket];
    printf("Bucket [%i]: ", bucket);
    unsigned int count = 0;


    while (node != NULL) {
      count++;
      node = node->next;
    }
    if (count < min) {
      min = count;
    }
    if (count > max) {
      max = count;
    }
    avg += count;

    printf("%i\n", count);
    
  }
  avg /= TABLE_SIZE;
  for (int bucket = 0; bucket < TABLE_SIZE; bucket++) {
    entry_t* node = hashtable->entries[bucket];
    unsigned int count = 0;
    while (node != NULL) { count++; node = node->next; }
    stddev += (count - avg) * (count-avg);
  }
  stddev /= TABLE_SIZE;
  stddev = sqrt(stddev);
  printf("Avg: %f\n", avg);
  printf("Std Dev: %f\n", stddev);

}

static int initiate(int chunksize) {
  if (initiated)
  {
    return -1; 
  }
  else
  {
    initiated = true;
    entity_chunks = create_ht();
    //we can bypass the <const> keyword by making a pointer to the <CHUNK_SIZE> variable and modifying it throught that.
    if (chunksize != CHUNK_SIZE) {
      return -1;
    }
    return 0;  
  }
}
static PyObject* init(PyObject* self,PyObject* chunk_size) {
  int chunksize;
  if (!PyArg_Parse(chunk_size,"i",&chunksize)) {
    return NULL; // return error if none found
  }
  if (initiate(chunksize) == -1) {
    // something bad happened
    PyErr_SetString(PyExc_RuntimeError, "Entity Manager Module was either initiated more than once or the entity_chunksize was changed in Python without changing it in C");
    return NULL;
  }
  Py_RETURN_NONE;
}


static PyObject* inclusive_range(PyObject* self, PyObject* arg) {
  int start,stop,step;
  if (!PyArg_ParseTuple(arg,"iii",&start,&stop,&step)) {
    return NULL; // return error if none found
  }
  Py_ssize_t length = 1;// Py_ssize_t is just a macro for __int64 on this machine
  int count = start;
  while (count < stop) {
    count += step;
    length++;
  }


  count = start;
  if (start == stop) {
    PyObject* tup = PyTuple_New(1);
    PyTuple_SET_ITEM(tup,0,Py_BuildValue("i",start));
    return tup;
  }
  PyObject* tup = PyTuple_New(length);
  for (int i = 0; i<length-1;i++){
    PyTuple_SET_ITEM(tup,i,Py_BuildValue("i",count));
    count += step;
  }
  PyTuple_SET_ITEM(tup,length-1,Py_BuildValue("i",stop));
  return tup;
  //x and y will now hold the position of the chunk submitted

}
// will return a "mathematical integer" of type <double>
static double get_irange_size(double start,double stop, double step) {
  return ceil((stop-start)/step) +1.0;
}
static PyObject* collided_chunks(PyObject* self, PyObject* args) {
  const double step = (double)CHUNK_SIZE;
  double left,top,right,bottom;
  if (!PyArg_ParseTuple(args,"dddd",&left,&top,&right,&bottom)) {
    return NULL; // return error if none found
  }
  double x_size = get_irange_size(left,right,step);
  double y_size = get_irange_size(top,bottom,step);
  


  int length = 0;
  int x = left;
  while (x < right) {
    x += step;
    length++;
  }
}


static PyMethodDef functions[] = {
  //"Python Name"                  C-Function Name     argument presentation      description
  //{"say_hello",                  exmod_say_hello,           METH_VARARGS,         "Say Hello from C and print message"},
  //{"init",                        (PyCFunction) init,                       METH_O,           "compute the nth fibonnaci number"},
  //{"addEntity",                   (PyCFunction) addNewEntity,                  METH_VARARGS,           "ADD BOODY"},
  //{"getEntitiesInChunk",          (PyCFunction) getEntitiesInChunk,         METH_VARARGS,     "ADD BOODY"},



  

  {"inclusive_range", (PyCFunction) inclusive_range, METH_VARARGS, "just like normal range but also includes the <stop> argument"},
  {NULL,NULL,0,NULL}  /* Sentinel */
};
static struct PyModuleDef module = { PyModuleDef_HEAD_INIT,"entity_manager","module docstring",-1,functions};

PyMODINIT_FUNC PyInit_entity_manager(void) {

  return PyModule_Create(&module);
}

// There be useless functions in the depths below
/*
static PyObject* addNewEntity(PyObject* self, PyObject* args) {
  PyObject* entity;
  int x,y;
  if (!PyArg_ParseTuple(args,"Oii",&entity,&x,&y)){
    return NULL;
  }
  printf("CHUNK TO BE IN is %d, %d",x,y);
  //x and y will now hold the position of the entity submitted
  linked_list_node* myList = ht_get(entity_chunks,x,y);
  if (myList == NULL){
    printf("CHunk had no previous entities in it so it is being created\n");

    //we know that that function hasn't been made yet so we have to make it
    myList = ll_create(entity);
    ht_set(entity_chunks,x,y,myList);
  }
  else {
    printf("Chunk exists so we are just adding it to the chunk\n");
    ll_add(myList,entity);
  }
  Py_RETURN_NONE;
}
static PyObject* getEntitiesInChunk(PyObject* self, PyObject* arg) {
  int cx,cy;
  if (!PyArg_ParseTuple(arg,"ii",&cx,&cy)) {
    return NULL; // return error if none found
  }
  //x and y will now hold the position of the chunk submitted
  linked_list_node* myList = ht_get(entity_chunks,cx,cy);
  printf("Got Chunk\n");
  if (myList == NULL) {
    printf("The chunk that you tried to get didn't have any entities\n");
    PyObject* list = PyList_New(0);
    
    return list;
  }
  else {
    printf("The chunk that you tried to get does have entities\n");
    PyObject* list = PyList_New(0);
    printf("creating a list\n");
    
    while (myList != NULL) {
      printf("Adding object to list %i\n",myList->object);
      PyList_Append(list,myList->object);
      myList = myList->next;
    }
    printf("returning list\n");
    return list;
  }
  Py_RETURN_NONE;
}
static PyObject* remove_entity(PyObject* self, PyObject* arg){
  PyObject* entity;
  if (!PyArg_Parse(arg,"O",&entity)){
    return NULL;
  }
    //chunk_pos = (entity.pos//CHUNK_SIZE).tuple
    //entity_chunks[chunk_pos].remove(entity)
  Py_RETURN_NONE;
}
*/